from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class UniFiError(RuntimeError):
    """Raised when UniFi discovery or normalization cannot proceed safely."""


@dataclass(frozen=True)
class UniFiConfig:
    base_url: str
    api_key: str
    site_id: str | None = None
    site_name: str | None = None
    verify_tls: bool = True
    ca_file: str | None = None
    timeout_seconds: float = 10.0

    @classmethod
    def from_values(
        cls,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        site_id: str | None = None,
        site_name: str | None = None,
        verify_tls: bool = True,
        ca_file: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> "UniFiConfig":
        raw_url = base_url or os.getenv("ROAD_UNIFI_URL") or os.getenv("UNIFI_URL")
        raw_key = api_key or os.getenv("ROAD_UNIFI_API_KEY") or os.getenv("UNIFI_API_KEY")
        if not raw_url:
            raise UniFiError("missing UniFi URL; pass --unifi-url or set ROAD_UNIFI_URL")
        if not raw_key:
            raise UniFiError(
                "missing UniFi API key; pass --unifi-api-key-env NAME or set ROAD_UNIFI_API_KEY"
            )

        resolved_site_id = site_id or os.getenv("ROAD_UNIFI_SITE_ID")
        resolved_site_name = site_name or os.getenv("ROAD_UNIFI_SITE_NAME")
        resolved_ca = ca_file or os.getenv("ROAD_UNIFI_CA_FILE")

        return cls(
            base_url=normalize_base_url(raw_url),
            api_key=raw_key,
            site_id=resolved_site_id,
            site_name=resolved_site_name,
            verify_tls=verify_tls,
            ca_file=resolved_ca,
            timeout_seconds=timeout_seconds,
        )

    def public(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "site_id": self.site_id,
            "site_name": self.site_name,
            "verify_tls": self.verify_tls,
            "ca_file_configured": bool(self.ca_file),
            "api_key_configured": bool(self.api_key),
        }


def normalize_base_url(raw: str) -> str:
    value = raw.strip().rstrip("/")
    if not value:
        raise UniFiError("empty UniFi URL")
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise UniFiError("UniFi URL must be an absolute http(s) URL")

    path = parsed.path.rstrip("/")
    if path.endswith("/proxy/network/integration") or path.endswith("/integration"):
        return value

    if path in {"", "/"}:
        # UniFi OS gateways mount the official Network Integration API here.
        return value + "/proxy/network/integration"

    raise UniFiError(
        "UniFi URL must be the gateway origin or an explicit .../integration base path"
    )


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def _version_tuple(value: Any) -> tuple[int, ...]:
    text = str(value or "")
    pieces: list[int] = []
    for token in text.split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        if not digits:
            break
        pieces.append(int(digits))
    return tuple(pieces)


def _extract_application_version(info: dict[str, Any]) -> str | None:
    for key in ("applicationVersion", "version"):
        if info.get(key):
            return str(info[key])
    data = info.get("data")
    if isinstance(data, dict):
        for key in ("applicationVersion", "version"):
            if data.get(key):
                return str(data[key])
    return None


def choose_site(
    sites: list[dict[str, Any]],
    *,
    site_id: str | None,
    site_name: str | None,
) -> dict[str, Any]:
    if site_id:
        matches = [site for site in sites if str(site.get("id")) == site_id]
        if len(matches) != 1:
            raise UniFiError(f"configured UniFi site id not found: {site_id}")
        return matches[0]

    if site_name:
        matches = [
            site
            for site in sites
            if str(site.get("name", "")).casefold() == site_name.casefold()
        ]
        if len(matches) != 1:
            raise UniFiError(
                f"configured UniFi site name must resolve exactly once: {site_name}"
            )
        return matches[0]

    if len(sites) == 1:
        return sites[0]
    if not sites:
        raise UniFiError("UniFi returned no sites")
    raise UniFiError(
        "multiple UniFi sites found; set ROAD_UNIFI_SITE_ID or ROAD_UNIFI_SITE_NAME"
    )


class UniFiClient:
    """Dependency-free client for the official UniFi Network Integration API."""

    def __init__(self, config: UniFiConfig):
        self.config = config

    def _context(self) -> ssl.SSLContext | None:
        if not self.config.base_url.startswith("https://"):
            return None
        if not self.config.verify_tls:
            return ssl._create_unverified_context()
        return ssl.create_default_context(cafile=self.config.ca_file)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
    ) -> Any:
        if not path.startswith("/"):
            raise UniFiError(f"invalid UniFi API path: {path}")

        data = None
        headers = {
            "Accept": "application/json",
            "X-API-Key": self.config.api_key,
            "User-Agent": "road-network/0.2",
        }
        if body is not None:
            data = json.dumps(body, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            self.config.base_url + path,
            data=data,
            headers=headers,
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.config.timeout_seconds,
                context=self._context(),
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            body_text = exc.read(2048).decode("utf-8", errors="replace")
            raise UniFiError(
                f"UniFi API {method.upper()} {path} returned HTTP {exc.code}: "
                f"{body_text[:500]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise UniFiError(
                f"could not reach UniFi API at {self.config.base_url}: {exc.reason}"
            ) from exc

        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise UniFiError(
                f"UniFi API {method.upper()} {path} returned non-JSON data"
            ) from exc

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def list_all(self, path: str) -> list[dict[str, Any]]:
        offset = 0
        limit = 200
        result: list[dict[str, Any]] = []
        while True:
            separator = "&" if "?" in path else "?"
            payload = self.get(f"{path}{separator}offset={offset}&limit={limit}")
            page = _items(payload)
            result.extend(page)

            if isinstance(payload, list):
                break
            if not isinstance(payload, dict):
                break
            total = payload.get("totalCount")
            count = payload.get("count")
            page_limit = payload.get("limit")
            if isinstance(total, int):
                if len(result) >= total:
                    break
            elif len(page) < limit:
                break

            step = (
                int(page_limit)
                if isinstance(page_limit, int) and page_limit > 0
                else int(count)
                if isinstance(count, int) and count > 0
                else len(page)
            )
            if step <= 0:
                break
            offset += step
        return result

    def discover(self) -> dict[str, Any]:
        info_raw = self.get("/v1/info")
        info = info_raw if isinstance(info_raw, dict) else {}
        sites = self.list_all("/v1/sites")
        site = choose_site(
            sites,
            site_id=self.config.site_id,
            site_name=self.config.site_name,
        )
        site_id = str(site.get("id") or "")
        if not site_id:
            raise UniFiError("selected UniFi site has no id")

        version = _extract_application_version(info)
        capabilities = {
            "application_version": version,
            "network_crud": _version_tuple(version) >= (10, 0, 162)
            if version
            else None,
            "firewall_zone_crud": _version_tuple(version) >= (10, 0, 162)
            if version
            else None,
            "firewall_policy_crud": _version_tuple(version) >= (10, 1, 84)
            if version
            else None,
        }

        networks = self.list_all(f"/v1/sites/{site_id}/networks")
        devices = self.list_all(f"/v1/sites/{site_id}/devices")
        clients = self.list_all(f"/v1/sites/{site_id}/clients")

        zones: list[dict[str, Any]] = []
        policies: list[dict[str, Any]] = []
        if capabilities["firewall_zone_crud"] is not False:
            zones = self.list_all(f"/v1/sites/{site_id}/firewall/zones")
        if capabilities["firewall_policy_crud"] is True:
            policies = self.list_all(f"/v1/sites/{site_id}/firewall/policies")

        return {
            "schema": "blackroad.unifi.observed.v1",
            "provider": "unifi",
            "connection": self.config.public(),
            "info": info,
            "site": site,
            "capabilities": capabilities,
            "networks": networks,
            "zones": zones,
            "policies": policies,
            "devices": devices,
            "clients": clients,
        }


def _network_vlan(network: dict[str, Any]) -> int | None:
    for key in ("vlanId", "vlan", "vlan_id"):
        value = network.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _network_name(network: dict[str, Any]) -> str:
    return str(network.get("name") or network.get("id") or "")


def _zone_name(zone: dict[str, Any]) -> str:
    return str(zone.get("name") or "")


def _provider_network_body(desired: dict[str, Any]) -> dict[str, Any]:
    # The v10 Integration API guarantees these fields. CIDR/gateway are intentionally
    # not invented here; the current official network schema does not expose those
    # settings in the same portable shape as BlackRoad canon.
    return {
        "management": "GATEWAY",
        "name": str(desired["id"]),
        "enabled": True,
        "vlanId": int(desired["vlan"]),
    }


def plan_unifi(desired: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    provider = desired.get("artifacts", {}).get("unifi", {})
    desired_networks = list(provider.get("networks") or [])
    live_networks = list(observed.get("networks") or [])
    live_zones = list(observed.get("zones") or [])

    by_name = {
        _network_name(item): item for item in live_networks if _network_name(item)
    }
    by_vlan: dict[int, list[dict[str, Any]]] = {}
    for item in live_networks:
        vlan = _network_vlan(item)
        if vlan is not None:
            by_vlan.setdefault(vlan, []).append(item)

    zone_by_name = {
        _zone_name(item): item for item in live_zones if _zone_name(item)
    }

    operations: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    warnings: list[str] = []

    capabilities = observed.get("capabilities") or {}
    if capabilities.get("network_crud") is False:
        blockers.append(
            {
                "resource": "provider:unifi",
                "reason": "unifi-network-version-too-old",
                "required": "Network 10.0.162+ for official network CRUD",
                "observed": capabilities.get("application_version"),
            }
        )

    for item in desired_networks:
        name = str(item["id"])
        vlan = int(item["vlan"])
        live = by_name.get(name)

        if live is None:
            vlan_matches = by_vlan.get(vlan, [])
            if vlan_matches:
                blockers.append(
                    {
                        "resource": f"network:{name}",
                        "reason": "vlan-already-owned-by-different-network",
                        "vlan": vlan,
                        "observed": [
                            {"id": match.get("id"), "name": _network_name(match)}
                            for match in vlan_matches
                        ],
                    }
                )
                continue
            operations.append(
                {
                    "action": "create",
                    "resource": f"network:{name}",
                    "provider": "unifi",
                    "body": _provider_network_body(item),
                    "canonical": item,
                    "requires": ["provider-write-ack", "post-write-readback"],
                }
            )
            continue

        live_vlan = _network_vlan(live)
        patch: dict[str, Any] = {}
        if live_vlan != vlan:
            patch["vlanId"] = vlan
        if live.get("enabled") is False:
            patch["enabled"] = True
        if patch:
            operations.append(
                {
                    "action": "update",
                    "resource": f"network:{name}",
                    "provider": "unifi",
                    "provider_id": live.get("id"),
                    "body": patch,
                    "canonical": item,
                    "requires": ["provider-write-ack", "post-write-readback"],
                }
            )

        live_id = live.get("id")
        zone = zone_by_name.get(name)
        if zone is None:
            operations.append(
                {
                    "action": "create",
                    "resource": f"zone:{name}",
                    "provider": "unifi",
                    "body": {"name": name, "networkIds": [live_id] if live_id else []},
                    "depends_on": f"network:{name}" if not live_id else None,
                    "requires": ["provider-write-ack", "post-write-readback"],
                }
            )
        elif live_id:
            network_ids = zone.get("networkIds")
            if not isinstance(network_ids, list):
                network_ids = []
            if live_id not in network_ids:
                operations.append(
                    {
                        "action": "update",
                        "resource": f"zone:{name}",
                        "provider": "unifi",
                        "provider_id": zone.get("id"),
                        "body": {
                            "networkIds": sorted(
                                {str(value) for value in network_ids if value}
                                | {str(live_id)}
                            )
                        },
                        "requires": ["provider-write-ack", "post-write-readback"],
                    }
                )

        # BlackRoad canon carries routed CIDR/gateway intent that the current
        # official Network endpoint cannot be assumed to mutate safely.
        if item.get("cidr") or item.get("gateway"):
            warnings.append(
                f"{name}: CIDR/gateway intent remains canon-only until the "
                "gateway's versioned API schema proves a writable mapping"
            )

    desired_names = {str(item["id"]) for item in desired_networks}
    unmanaged = [
        {"id": item.get("id"), "name": _network_name(item), "vlan": _network_vlan(item)}
        for item in live_networks
        if _network_name(item) not in desired_names
    ]

    return {
        "schema": "blackroad.unifi.plan.v1",
        "provider": "unifi",
        "site": observed.get("site"),
        "application_version": capabilities.get("application_version"),
        "desired_digest": desired.get("digest"),
        "changes": len(operations),
        "operations": operations,
        "blockers": blockers,
        "warnings": sorted(set(warnings)),
        "unmanaged_observed_networks": unmanaged,
        "destructive_operations": 0,
        "provider_write_enabled": False,
        "safe_read_only": True,
    }
