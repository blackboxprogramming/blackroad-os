from __future__ import annotations

import hashlib
import ipaddress
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .yamlmini import parse_simple_yaml

CANON_FILENAMES = ("networks.yaml", "devices.yaml", "services.yaml", "bindings.yaml", "policy.yaml")


class CanonError(RuntimeError):
    pass


def canonical_network_dir(root: Path) -> Path:
    root = root.resolve()
    for candidate in (root, root / "Canon" / "Network"):
        if all((candidate / name).is_file() for name in CANON_FILENAMES):
            return candidate
    raise CanonError(f"could not locate Canon/Network under {root}")


def load_canon(root: Path) -> dict[str, Any]:
    network_dir = canonical_network_dir(root)
    docs: dict[str, Any] = {}
    for filename in CANON_FILENAMES:
        path = network_dir / filename
        try:
            docs[filename.removesuffix(".yaml")] = parse_simple_yaml(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CanonError(f"{path}: {exc}") from exc
    docs["_network_dir"] = str(network_dir)
    return docs


def _all_devices(canon: dict[str, Any]) -> list[dict[str, Any]]:
    doc = canon["devices"]
    return list(doc.get("devices") or []) + list(doc.get("unresolved") or [])


def validate_canon(canon: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    networks = list(canon["networks"].get("networks") or [])
    by_network: dict[str, dict[str, Any]] = {}
    seen_vlans: dict[int, str] = {}

    for network in networks:
        network_id = str(network.get("id", ""))
        if not network_id:
            errors.append("network without id")
            continue
        if network_id in by_network:
            errors.append(f"duplicate network id: {network_id}")
        by_network[network_id] = network

        vlan = network.get("vlan")
        if not isinstance(vlan, int):
            errors.append(f"{network_id}: vlan must be an integer")
        elif vlan in seen_vlans:
            errors.append(f"duplicate vlan {vlan}: {seen_vlans[vlan]} and {network_id}")
        else:
            seen_vlans[vlan] = network_id

        try:
            subnet = ipaddress.ip_network(str(network.get("cidr")), strict=True)
            gateway = ipaddress.ip_address(str(network.get("gateway")))
            if gateway not in subnet:
                errors.append(f"{network_id}: gateway {gateway} is outside {subnet}")
        except ValueError as exc:
            errors.append(f"{network_id}: invalid CIDR/gateway: {exc}")

    control = by_network.get("road.control")
    if not control:
        errors.append("missing road.control network")
    else:
        if control.get("vlan") != 1729:
            errors.append("road.control must use VLAN 1729")
        if control.get("cidr") != "10.17.29.0/24":
            warnings.append("road.control CIDR differs from canonical 10.17.29.0/24")

    if "road.lab" not in by_network:
        errors.append("missing road.lab network")

    devices = _all_devices(canon)
    device_ids: dict[str, dict[str, Any]] = {}
    assigned_ips: dict[str, str] = {}

    for device in devices:
        device_id = str(device.get("id", ""))
        if not device_id:
            errors.append("device without id")
            continue
        if device_id in device_ids:
            errors.append(f"duplicate device id: {device_id}")
        device_ids[device_id] = device

        network_id = str(device.get("network", ""))
        network = by_network.get(network_id)
        if network is None:
            errors.append(f"{device_id}: unknown network {network_id}")
            continue

        ipv4 = device.get("ipv4")
        if ipv4 is not None:
            try:
                address = ipaddress.ip_address(str(ipv4))
                subnet = ipaddress.ip_network(str(network["cidr"]), strict=True)
                if address not in subnet:
                    errors.append(f"{device_id}: {address} is outside {network_id} {subnet}")
                key = str(address)
                prior = assigned_ips.get(key)
                gateway_match = str(network.get("gateway")) == key and device.get("role") == "edge-gateway"
                if prior and not gateway_match:
                    errors.append(f"duplicate device IP {key}: {prior} and {device_id}")
                else:
                    assigned_ips[key] = device_id
            except ValueError as exc:
                errors.append(f"{device_id}: invalid ipv4 {ipv4}: {exc}")

        target_network = device.get("target_network")
        target_ipv4 = device.get("target_ipv4")
        if target_network or target_ipv4:
            target = by_network.get(str(target_network))
            if target is None:
                errors.append(f"{device_id}: unknown target network {target_network}")
            elif target_ipv4:
                try:
                    address = ipaddress.ip_address(str(target_ipv4))
                    subnet = ipaddress.ip_network(str(target["cidr"]), strict=True)
                    if address not in subnet:
                        errors.append(f"{device_id}: target {address} is outside {target_network} {subnet}")
                except ValueError as exc:
                    errors.append(f"{device_id}: invalid target_ipv4 {target_ipv4}: {exc}")

    for unresolved in canon["devices"].get("unresolved") or []:
        if unresolved.get("network") != "road.lab":
            errors.append(f"{unresolved.get('id')}: unresolved devices must remain in road.lab")

    service_ips: dict[str, str] = {}
    for section, expected_network in (("services", "road.services"), ("control", "road.control")):
        network = by_network.get(expected_network)
        if not network:
            continue
        subnet = ipaddress.ip_network(str(network["cidr"]), strict=True)
        for service in canon["services"].get(section) or []:
            service_id = str(service.get("id", ""))
            try:
                address = ipaddress.ip_address(str(service.get("ipv4")))
                if address not in subnet:
                    errors.append(f"{service_id}: {address} is outside {expected_network} {subnet}")
                key = str(address)
                if key in service_ips:
                    errors.append(f"duplicate service IP {key}: {service_ips[key]} and {service_id}")
                service_ips[key] = service_id
            except ValueError as exc:
                errors.append(f"{service_id}: invalid service address: {exc}")

    agents: set[str] = set()
    for binding in canon["bindings"].get("bindings") or []:
        agent = str(binding.get("agent", ""))
        device = str(binding.get("device", ""))
        if not agent:
            errors.append("binding without agent")
        elif agent in agents:
            errors.append(f"duplicate agent binding: {agent}")
        agents.add(agent)
        if device not in device_ids:
            errors.append(f"{agent}: binding references unknown device {device}")

    defaults = canon["policy"].get("defaults") or {}
    if defaults.get("interzone") != "deny":
        errors.append("policy defaults.interzone must be deny")
    if defaults.get("unknown_device_network") != "road.lab":
        errors.append("policy defaults.unknown_device_network must be road.lab")

    return {"errors": errors, "warnings": warnings}


def _dns_records(canon: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for device in _all_devices(canon):
        if device.get("dns") and device.get("ipv4"):
            records.append(
                {
                    "name": str(device["dns"]),
                    "type": "A",
                    "value": str(device["ipv4"]),
                    "owner": str(device["id"]),
                }
            )
    for section in ("services", "control"):
        for service in canon["services"].get(section) or []:
            if service.get("dns") and service.get("ipv4"):
                records.append(
                    {
                        "name": str(service["dns"]),
                        "type": "A",
                        "value": str(service["ipv4"]),
                        "owner": str(service["id"]),
                    }
                )
    return sorted(records, key=lambda item: item["name"])


def compile_state(canon: dict[str, Any]) -> dict[str, Any]:
    report = validate_canon(canon)
    if report["errors"]:
        raise CanonError("canon validation failed:\n- " + "\n- ".join(report["errors"]))

    networks = list(canon["networks"].get("networks") or [])
    devices = _all_devices(canon)
    services = list(canon["services"].get("services") or [])
    control = list(canon["services"].get("control") or [])
    bindings = list(canon["bindings"].get("bindings") or [])
    zones = canon["policy"].get("zones") or {}

    provider = {
        "schema": "blackroad.network.provider-plan.v1",
        "adapter": "unifi",
        "networks": [
            {
                "id": item["id"],
                "vlan": item["vlan"],
                "cidr": item["cidr"],
                "gateway": item["gateway"],
                "trust": item.get("trust"),
                "zone": item["id"],
            }
            for item in networks
        ],
        "zones": zones,
        "default_interzone": "deny",
        "note": "Provider-neutral desired state. Live UniFi mutation requires an authenticated adapter.",
    }

    fleet = {"schema": "blackroad.fleet.compiled.v1", "devices": devices}
    dns = {"schema": "blackroad.dns.compiled.v1", "records": _dns_records(canon)}
    service_state = {"schema": "blackroad.services.compiled.v1", "services": services, "control": control}
    binding_state = {
        "schema": "blackroad.bindings.compiled.v1",
        "bindings": bindings,
        "invariants": canon["bindings"].get("invariants") or [],
    }

    resources: dict[str, Any] = {}
    for item in networks:
        resources[f"network:{item['id']}"] = item
    for item in devices:
        resources[f"device:{item['id']}"] = item
    for item in services + control:
        resources[f"service:{item['id']}"] = item
    for item in dns["records"]:
        resources[f"dns:{item['name']}"] = item
    for item in bindings:
        resources[f"binding:{item['agent']}"] = item
    for name, zone in zones.items():
        resources[f"zone:{name}"] = zone

    digest = hashlib.sha256(
        json.dumps(resources, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": "blackroad.network.compiled.v1",
        "digest": f"sha256:{digest}",
        "artifacts": {
            "unifi": provider,
            "dns": dns,
            "fleet": fleet,
            "services": service_state,
            "bindings": binding_state,
        },
        "resources": resources,
        "warnings": report["warnings"],
    }


def load_current_state(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"resources": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonError(f"could not read current state {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("resources", {}), dict):
        raise CanonError(f"invalid current state: {path}")
    return data


def plan_changes(desired: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    desired_resources = desired.get("resources") or {}
    current_resources = current.get("resources") or {}
    operations: list[dict[str, Any]] = []

    for key in sorted(desired_resources.keys() - current_resources.keys()):
        operations.append({"action": "create", "resource": key, "desired": desired_resources[key]})
    for key in sorted(desired_resources.keys() & current_resources.keys()):
        if desired_resources[key] != current_resources[key]:
            operations.append(
                {
                    "action": "update",
                    "resource": key,
                    "current": current_resources[key],
                    "desired": desired_resources[key],
                }
            )
    for key in sorted(current_resources.keys() - desired_resources.keys()):
        operations.append({"action": "delete", "resource": key, "current": current_resources[key]})

    return {
        "schema": "blackroad.network.plan.v1",
        "desired_digest": desired["digest"],
        "changes": len(operations),
        "operations": operations,
        "safe_to_apply_locally": True,
        "live_provider_apply": False,
    }


def _atomic_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(body, encoding="utf-8")
    os.replace(temporary, path)


def apply_local(
    desired: dict[str, Any], output_dir: Path, receipt_dir: Path | None = None
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in desired["artifacts"].items():
        _atomic_write(output_dir / f"{name}.json", payload)
    _atomic_write(output_dir / "state.json", desired)

    now = datetime.now(timezone.utc)
    receipt = {
        "schema": "blackroad.roadchain.network-apply.v1",
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "mode": "local-compile",
        "desired_digest": desired["digest"],
        "output_dir": str(output_dir),
        "provider_mutated": False,
        "result": "compiled",
    }
    receipt_root = receipt_dir.resolve() if receipt_dir else output_dir / "receipts"
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    receipt_path = receipt_root / f"network-apply-{stamp}.json"
    _atomic_write(receipt_path, receipt)
    receipt["receipt_path"] = str(receipt_path)
    return receipt
