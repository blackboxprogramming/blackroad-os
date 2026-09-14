from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .compiler import (
    CanonError,
    apply_local,
    compile_state,
    load_canon,
    load_current_state,
    plan_changes,
    validate_canon,
)
from .unifi import UniFiClient, UniFiConfig, UniFiError, plan_unifi

EXIT_OK = 0
EXIT_CHANGES = 10
EXIT_BLOCKED = 20


def _emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                print(f"{key}: {json.dumps(value, sort_keys=True)}")
            else:
                print(f"{key}: {value}")
    else:
        print(payload)


def _canon(args: argparse.Namespace) -> dict[str, Any]:
    return load_canon(Path(args.root))


def _write_json(path: Path, payload: Any) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _unifi_config(args: argparse.Namespace) -> UniFiConfig:
    env_name = getattr(args, "unifi_api_key_env", "ROAD_UNIFI_API_KEY")
    api_key = os.getenv(env_name)
    if not api_key:
        raise UniFiError(
            f"environment variable {env_name} is not set; API keys are intentionally "
            "not accepted as command-line values"
        )
    return UniFiConfig.from_values(
        base_url=getattr(args, "unifi_url", None),
        api_key=api_key,
        site_id=getattr(args, "unifi_site_id", None),
        site_name=getattr(args, "unifi_site_name", None),
        verify_tls=not getattr(args, "unifi_insecure", False),
        ca_file=getattr(args, "unifi_ca_file", None),
        timeout_seconds=float(getattr(args, "unifi_timeout", 10.0)),
    )


def _discover_unifi(args: argparse.Namespace) -> dict[str, Any]:
    config = _unifi_config(args)
    observed = UniFiClient(config).discover()
    snapshot = getattr(args, "snapshot", None)
    if snapshot:
        _write_json(Path(snapshot), observed)
    return observed


def _unifi_summary(observed: dict[str, Any]) -> dict[str, Any]:
    capabilities = observed.get("capabilities") or {}
    site = observed.get("site") or {}
    return {
        "status": "observed",
        "provider": "unifi",
        "site": {"id": site.get("id"), "name": site.get("name")},
        "application_version": capabilities.get("application_version"),
        "capabilities": capabilities,
        "counts": {
            "networks": len(observed.get("networks") or []),
            "zones": len(observed.get("zones") or []),
            "policies": len(observed.get("policies") or []),
            "devices": len(observed.get("devices") or []),
            "clients": len(observed.get("clients") or []),
        },
        "connection": observed.get("connection"),
    }


def command_validate(args: argparse.Namespace) -> int:
    canon = _canon(args)
    report = validate_canon(canon)
    payload = {
        "status": "valid" if not report["errors"] else "invalid",
        "errors": report["errors"],
        "warnings": report["warnings"],
        "canon": canon["_network_dir"],
    }
    _emit(payload, args.json)
    return EXIT_OK if not report["errors"] else EXIT_BLOCKED


def command_discover(args: argparse.Namespace) -> int:
    observed = _discover_unifi(args)
    payload = observed if args.full else _unifi_summary(observed)
    if args.snapshot:
        payload = {
            **payload,
            "snapshot": str(Path(args.snapshot).expanduser().resolve()),
        }
    _emit(payload, args.json)
    return EXIT_OK


def _desired_and_local_plan(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any]]:
    desired = compile_state(_canon(args))
    state_path = Path(args.state) if args.state else Path(args.output) / "state.json"
    current = load_current_state(state_path)
    return desired, plan_changes(desired, current)


def command_plan(args: argparse.Namespace) -> int:
    if args.adapter == "unifi":
        desired = compile_state(_canon(args))
        observed = _discover_unifi(args)
        plan = plan_unifi(desired, observed)
        payload = {
            "status": (
                "blocked"
                if plan["blockers"]
                else "changes"
                if plan["changes"]
                else "clean"
            ),
            "digest": desired["digest"],
            **plan,
        }
        _emit(payload, args.json)
        if plan["blockers"]:
            return EXIT_BLOCKED
        return EXIT_CHANGES if plan["changes"] else EXIT_OK

    desired, plan = _desired_and_local_plan(args)
    payload = {
        "status": "changes" if plan["changes"] else "clean",
        "digest": desired["digest"],
        "warnings": desired["warnings"],
        **plan,
    }
    _emit(payload, args.json)
    return EXIT_CHANGES if plan["changes"] else EXIT_OK


def command_apply(args: argparse.Namespace) -> int:
    if args.adapter == "unifi":
        desired = compile_state(_canon(args))
        observed = _discover_unifi(args)
        plan = plan_unifi(desired, observed)
        if plan["blockers"]:
            _emit({"status": "blocked", "adapter": "unifi", "plan": plan}, args.json)
            return EXIT_BLOCKED
        if args.execute:
            payload = {
                "status": "blocked",
                "adapter": "unifi",
                "reason": "provider-write-phase-not-enabled",
                "detail": (
                    "The official read/discovery adapter is live, but provider mutation "
                    "remains disabled until the enrolled Dream Router's versioned schema "
                    "is captured and write/readback tests pass. No mutation was attempted."
                ),
                "provider_mutated": False,
                "plan": plan,
            }
            _emit(payload, args.json)
            return EXIT_BLOCKED

        payload = {
            "status": "dry-run",
            "adapter": "unifi",
            "provider_mutated": False,
            "plan": plan,
        }
        _emit(payload, args.json)
        return EXIT_CHANGES if plan["changes"] else EXIT_OK

    desired, plan = _desired_and_local_plan(args)

    if not args.execute:
        payload = {
            "status": "dry-run",
            "adapter": "local",
            "instruction": (
                "re-run with --execute to write compiled artifacts and a RoadChain receipt"
            ),
            "plan": plan,
        }
        _emit(payload, args.json)
        return EXIT_CHANGES if plan["changes"] else EXIT_OK

    receipt = apply_local(
        desired,
        Path(args.output),
        Path(args.receipt_dir) if args.receipt_dir else None,
    )
    payload = {
        "status": "compiled",
        "adapter": "local",
        "changes": plan["changes"],
        "digest": desired["digest"],
        "receipt": receipt,
    }
    _emit(payload, args.json)
    return EXIT_OK


def _add_unifi_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--unifi-url",
        help=(
            "UniFi gateway origin or explicit Integration API base; "
            "defaults to ROAD_UNIFI_URL"
        ),
    )
    parser.add_argument(
        "--unifi-api-key-env",
        default="ROAD_UNIFI_API_KEY",
        help=(
            "environment variable containing the API key; command-line secrets are "
            "intentionally unsupported"
        ),
    )
    parser.add_argument("--unifi-site-id", help="explicit UniFi site UUID")
    parser.add_argument("--unifi-site-name", help="explicit UniFi site name")
    parser.add_argument("--unifi-ca-file", help="custom CA bundle for local TLS")
    parser.add_argument(
        "--unifi-insecure",
        action="store_true",
        help="disable TLS certificate verification (lab/recovery only)",
    )
    parser.add_argument(
        "--unifi-timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--snapshot",
        help="optional local path for the full observed UniFi snapshot",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="road-network",
        description="Validate, discover, plan, and compile BlackRoad network canon.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--root",
        default=".",
        help="repository root or Canon/Network directory",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")

    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate network canon invariants")
    validate.set_defaults(func=command_validate)

    discover = commands.add_parser(
        "discover",
        help="read current provider state without mutation",
    )
    discover.add_argument("--adapter", choices=("unifi",), default="unifi")
    discover.add_argument(
        "--full",
        action="store_true",
        help="emit full observed provider payload instead of a redacted summary",
    )
    _add_unifi_args(discover)
    discover.set_defaults(func=command_discover)

    plan = commands.add_parser("plan", help="diff canon against current state")
    plan.add_argument("--adapter", choices=("local", "unifi"), default="local")
    plan.add_argument("--state", help="explicit current state.json path for local mode")
    plan.add_argument(
        "--output",
        default=".road/network",
        help="compiled-state directory for local mode",
    )
    _add_unifi_args(plan)
    plan.set_defaults(func=command_plan)

    apply = commands.add_parser("apply", help="compile/apply desired network state")
    apply.add_argument("--state", help="explicit current state.json path")
    apply.add_argument(
        "--output",
        default=".road/network",
        help="compiled-state directory",
    )
    apply.add_argument("--receipt-dir", help="optional receipt output directory")
    apply.add_argument("--adapter", choices=("local", "unifi"), default="local")
    apply.add_argument(
        "--execute",
        action="store_true",
        help="perform the selected adapter's write phase when supported",
    )
    _add_unifi_args(apply)
    apply.set_defaults(func=command_apply)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (CanonError, UniFiError) as exc:
        _emit(
            {"status": "blocked", "error": str(exc)},
            getattr(args, "json", False),
        )
        return EXIT_BLOCKED
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
