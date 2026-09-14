from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .compiler import CanonError, apply_local, compile_state, load_canon, load_current_state, plan_changes, validate_canon

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


def _desired_and_plan(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    desired = compile_state(_canon(args))
    state_path = Path(args.state) if args.state else Path(args.output) / "state.json"
    current = load_current_state(state_path)
    return desired, plan_changes(desired, current)


def command_plan(args: argparse.Namespace) -> int:
    desired, plan = _desired_and_plan(args)
    payload = {
        "status": "changes" if plan["changes"] else "clean",
        "digest": desired["digest"],
        "warnings": desired["warnings"],
        **plan,
    }
    _emit(payload, args.json)
    return EXIT_CHANGES if plan["changes"] else EXIT_OK


def command_apply(args: argparse.Namespace) -> int:
    desired, plan = _desired_and_plan(args)

    if args.adapter == "unifi":
        payload = {
            "status": "blocked",
            "reason": "live UniFi adapter is intentionally not implemented yet",
            "detail": "The router is not enrolled and no authenticated provider session exists. Compile local desired state first; do not fake provider mutation.",
            "plan": plan,
        }
        _emit(payload, args.json)
        return EXIT_BLOCKED

    if not args.execute:
        payload = {
            "status": "dry-run",
            "adapter": "local",
            "instruction": "re-run with --execute to write compiled artifacts and a RoadChain receipt",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="road-network",
        description="Validate, plan, and compile BlackRoad network canon.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--root", default=".", help="repository root or Canon/Network directory")
    parser.add_argument("--json", action="store_true", help="machine-readable output")

    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate network canon invariants")
    validate.set_defaults(func=command_validate)

    plan = commands.add_parser("plan", help="diff canon against compiled state")
    plan.add_argument("--state", help="explicit current state.json path")
    plan.add_argument("--output", default=".road/network", help="compiled-state directory")
    plan.set_defaults(func=command_plan)

    apply = commands.add_parser("apply", help="compile/apply desired network state")
    apply.add_argument("--state", help="explicit current state.json path")
    apply.add_argument("--output", default=".road/network", help="compiled-state directory")
    apply.add_argument("--receipt-dir", help="optional receipt output directory")
    apply.add_argument("--adapter", choices=("local", "unifi"), default="local")
    apply.add_argument("--execute", action="store_true", help="perform local compiled-state write")
    apply.set_defaults(func=command_apply)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except CanonError as exc:
        _emit({"status": "blocked", "error": str(exc)}, getattr(args, "json", False))
        return EXIT_BLOCKED
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
