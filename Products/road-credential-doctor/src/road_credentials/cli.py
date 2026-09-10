from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from . import __version__
from .catalog import connector_catalog
from .config import ConfigError, load_config
from .doctor import run_doctor
from .inventory import blockers_for_credentials, coverage_report
from .models import Credential, Finding, Settings
from .policy import RISK_RANK, risk_allows
from .rotation import reconcile_pending, rotate
from .scanner import ScanIncomplete, scan
from .state import RotationBusy, load_state


EXIT_OK = 0
EXIT_FINDINGS = 10
EXIT_BLOCKED = 20
EXIT_ROTATION_FAILED = 30


def _print(payload: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {value}")
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                details = " ".join(f"{key}={value}" for key, value in item.items() if value is not None)
                print(details)
            else:
                print(item)
    else:
        print(payload)


def _retired(settings: Settings) -> set[str]:
    return set(load_state(settings.state_file).get("retired_fingerprints", []))


def _public_findings(settings: Settings, findings: list[Finding]) -> list[dict[str, Any]]:
    retired = _retired(settings)
    return [finding.public(retired=finding.fingerprint in retired) for finding in findings]


def _mapping(settings: Settings, findings: list[Finding]) -> tuple[dict[str, list[Finding]], list[dict[str, Any]]]:
    retired = _retired(settings)
    grouped: dict[str, list[Finding]] = defaultdict(list)
    blocked: list[dict[str, Any]] = []
    for finding in findings:
        if finding.fingerprint in retired:
            continue
        matches = [credential for credential in settings.credentials if credential.matches(finding)]
        if len(matches) == 1:
            grouped[matches[0].id].append(finding)
        else:
            blocked.append(
                {
                    **finding.public(),
                    "reason": "unmapped" if not matches else "ambiguous",
                    "matching_credentials": [credential.id for credential in matches],
                }
            )
    return dict(grouped), blocked


def command_scan(args: argparse.Namespace, settings: Settings) -> int:
    findings = scan(settings, include_history=args.git_history)
    public = _public_findings(settings, findings)
    _print({"count": len(public), "findings": public}, as_json=args.json)
    return EXIT_FINDINGS if any(item["status"] == "active" for item in public) else EXIT_OK


def command_doctor(args: argparse.Namespace, settings: Settings) -> int:
    checks = run_doctor(settings, repair=args.repair)
    findings = scan(settings, include_history=args.git_history)
    public = _public_findings(settings, findings)
    state = load_state(settings.state_file)
    coverage = coverage_report(settings)
    payload = {
        "checks": [check.public() for check in checks],
        "active_leaks": sum(item["status"] == "active" for item in public),
        "retired_leaks_to_remove": sum(item["status"] == "retired" for item in public),
        "pending_revocations": len(state.get("pending_revocations", [])),
        "consumer_coverage": coverage,
        "findings": public,
    }
    _print(payload, as_json=args.json)
    if any(check.level == "error" for check in checks):
        return EXIT_BLOCKED
    if coverage["uncovered"] or coverage["unregistered"] or coverage["ambiguous"]:
        return EXIT_BLOCKED
    if payload["active_leaks"] or payload["pending_revocations"]:
        return EXIT_FINDINGS
    return EXIT_OK


def command_inventory(args: argparse.Namespace, settings: Settings) -> int:
    report = coverage_report(settings)
    _print(report, as_json=args.json)
    blocked = bool(report["uncovered"] or report["unregistered"] or report["ambiguous"])
    return EXIT_BLOCKED if blocked else EXIT_OK


def command_connectors(args: argparse.Namespace, _settings: Settings | None) -> int:
    _print(connector_catalog(), as_json=args.json)
    return EXIT_OK


def _selected_credentials(
    settings: Settings,
    grouped: dict[str, list[Finding]],
    requested: list[str],
    rotate_all: bool,
    force: bool,
) -> list[tuple[Credential, list[Finding]]]:
    by_id = {credential.id: credential for credential in settings.credentials}
    selected_ids = sorted(grouped) if rotate_all else requested
    selected: list[tuple[Credential, list[Finding]]] = []
    for credential_id in selected_ids:
        credential = by_id.get(credential_id)
        if credential is None:
            raise ConfigError(f"unknown credential: {credential_id}")
        findings = grouped.get(credential_id, [])
        if findings or force:
            selected.append((credential, findings))
    return selected


def command_heal(args: argparse.Namespace, settings: Settings) -> int:
    checks = run_doctor(settings)
    errors = [check.public() for check in checks if check.level == "error"]
    findings = scan(settings, include_history=args.git_history)
    grouped, blocked = _mapping(settings, findings)
    try:
        selected = _selected_credentials(settings, grouped, args.credential, args.all, args.force)
    except ConfigError as exc:
        _print({"status": "blocked", "error": str(exc)}, as_json=args.json)
        return EXIT_BLOCKED
    selected_ids = {credential.id for credential, _items in selected}
    coverage = coverage_report(settings)
    coverage_blockers = blockers_for_credentials(coverage, selected_ids, include_unregistered=args.all)
    risk_blockers = [
        {"credential_id": credential.id, "risk": credential.risk, "approved_through": args.approve_risk}
        for credential, _items in selected
        if not risk_allows(credential.risk, args.approve_risk)
    ]
    plan = {
        "mode": "execute" if args.execute else "dry_run",
        "credentials": [
            {
                "id": credential.id,
                "connector": credential.connector,
                "risk": credential.risk,
                "finding_count": len(items),
                "consumers": [consumer.id for consumer in credential.consumers],
                "execution_plane": "connector",
                "sequence": ["create", "validate", "update", "verify", "activate", "revoke_old"],
            }
            for credential, items in selected
        ],
        "blocked_findings": blocked,
        "consumer_coverage_blockers": coverage_blockers,
        "risk_approval_blockers": risk_blockers,
        "configuration_errors": errors,
    }
    if not args.execute:
        _print(plan, as_json=args.json)
        return EXIT_BLOCKED if blocked or coverage_blockers or errors else (EXIT_FINDINGS if selected else EXIT_OK)
    if not args.ack_keep_access:
        _print(
            {"status": "blocked", "error": "--ack-keep-access is required for live rotation", "plan": plan},
            as_json=args.json,
        )
        return EXIT_BLOCKED
    if errors or blocked or coverage_blockers or risk_blockers:
        _print({"status": "blocked", "plan": plan}, as_json=args.json)
        return EXIT_BLOCKED
    outcomes = [rotate(settings, credential, items, approved_risk=args.approve_risk).public() for credential, items in selected]
    _print({"status": "complete", "outcomes": outcomes}, as_json=args.json)
    failed = any(item["status"].startswith("failed") or item["status"] == "pending_revocation" for item in outcomes)
    return EXIT_ROTATION_FAILED if failed else EXIT_OK


def command_reconcile(args: argparse.Namespace, settings: Settings) -> int:
    if not args.execute or not args.ack_keep_access:
        _print(
            {"status": "blocked", "error": "reconcile requires --execute --ack-keep-access"},
            as_json=args.json,
        )
        return EXIT_BLOCKED
    configuration_errors = [check.public() for check in run_doctor(settings) if check.level == "error"]
    if configuration_errors:
        _print({"status": "blocked", "configuration_errors": configuration_errors}, as_json=args.json)
        return EXIT_BLOCKED
    state = load_state(settings.state_file)
    pending_ids = {str(item.get("credential_id")) for item in state.get("pending_revocations", [])}
    risk_blockers = [
        {"credential_id": credential.id, "risk": credential.risk, "approved_through": args.approve_risk}
        for credential in settings.credentials
        if credential.id in pending_ids and not risk_allows(credential.risk, args.approve_risk)
    ]
    if risk_blockers:
        _print({"status": "blocked", "risk_approval_blockers": risk_blockers}, as_json=args.json)
        return EXIT_BLOCKED
    outcomes = []
    for credential in settings.credentials:
        if credential.id in pending_ids:
            outcomes.extend(item.public() for item in reconcile_pending(settings, credential, approved_risk=args.approve_risk))
    _print({"status": "complete", "outcomes": outcomes}, as_json=args.json)
    return EXIT_ROTATION_FAILED if any(item["status"] == "pending_revocation" for item in outcomes) else EXIT_OK


def command_watch(args: argparse.Namespace, settings: Settings) -> int:
    if args.execute and not args.ack_keep_access:
        _print({"status": "blocked", "error": "watch --execute requires --ack-keep-access"}, as_json=args.json)
        return EXIT_BLOCKED
    configuration_errors = [check.public() for check in run_doctor(settings) if check.level == "error"]
    if args.execute and configuration_errors:
        _print({"status": "blocked", "configuration_errors": configuration_errors}, as_json=args.json)
        return EXIT_BLOCKED
    stopping = False

    def stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    cycle = 0
    last_code = EXIT_OK
    while not stopping and (args.max_cycles == 0 or cycle < args.max_cycles):
        cycle += 1
        findings = scan(settings, include_history=args.git_history)
        grouped, blocked = _mapping(settings, findings)
        pending_ids = {
            str(item.get("credential_id"))
            for item in load_state(settings.state_file).get("pending_revocations", [])
        }
        eligible_ids = {
            credential.id for credential in settings.credentials
            if credential.auto_heal and risk_allows(credential.risk, "medium")
        }
        deferred_pending = sorted(pending_ids - eligible_ids)
        auto_ids = {
            credential_id for credential_id in eligible_ids
            if credential_id in grouped or credential_id in pending_ids
        }
        coverage = coverage_report(settings)
        coverage_blockers = blockers_for_credentials(coverage, auto_ids, include_unregistered=True)
        outcomes = []
        if args.execute and not blocked and not coverage_blockers:
            for credential in settings.credentials:
                if credential.id in eligible_ids and credential.id in pending_ids:
                    outcomes.extend(item.public() for item in reconcile_pending(settings, credential, approved_risk="medium"))
            for credential in settings.credentials:
                # Findings were mapped before recovery; defer a fresh rotation until
                # the next scan so retired fingerprints cannot create another key.
                if credential.id in eligible_ids and credential.id in grouped and credential.id not in pending_ids:
                    outcomes.append(rotate(settings, credential, grouped[credential.id], approved_risk="medium").public())
        payload = {
            "cycle": cycle,
            "active_findings": sum(len(items) for items in grouped.values()),
            "blocked_findings": blocked,
            "consumer_coverage_blockers": coverage_blockers,
            "deferred_pending_credentials": deferred_pending,
            "outcomes": outcomes,
        }
        _print(payload, as_json=args.json)
        if blocked or coverage_blockers or deferred_pending or any(item["status"].startswith("failed") or item["status"] == "pending_revocation" for item in outcomes):
            last_code = EXIT_ROTATION_FAILED
        if not stopping and (args.max_cycles == 0 or cycle < args.max_cycles):
            time.sleep(args.interval)
    return last_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="road-credentials", description="Detect leaks and request connector-side rotation without lockout")
    parser.add_argument("--config", default="credentials.json", help="path to credential lifecycle configuration")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output without secret values")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="find credential material without printing values")
    scan_parser.add_argument("--git-history", action="store_true")
    scan_parser.set_defaults(handler=command_scan)

    inventory_parser = subparsers.add_parser("inventory", help="prove every secret reference has a declared consumer")
    inventory_parser.set_defaults(handler=command_inventory)

    connectors_parser = subparsers.add_parser("connectors", help="show managed and user-managed connector policies")
    connectors_parser.set_defaults(handler=command_connectors)

    doctor_parser = subparsers.add_parser("doctor", help="check connector transport, state, receipts, and leaks")
    doctor_parser.add_argument("--git-history", action="store_true")
    doctor_parser.add_argument("--repair", action="store_true", help="repair only local runtime permissions/directories")
    doctor_parser.set_defaults(handler=command_doctor)

    heal_parser = subparsers.add_parser("heal", help="plan or dispatch connector-side no-lockout rotation")
    selection = heal_parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="rotate every uniquely mapped active leak")
    selection.add_argument("--credential", action="append", default=[], help="credential id to rotate")
    heal_parser.add_argument("--git-history", action="store_true")
    heal_parser.add_argument("--force", action="store_true", help="rotate selected credential even without a detected leak")
    heal_parser.add_argument("--execute", action="store_true", help="dispatch live lifecycle actions to the connector host")
    heal_parser.add_argument("--ack-keep-access", action="store_true", help="acknowledge staged live rotation and rollback policy")
    heal_parser.add_argument("--approve-risk", choices=tuple(RISK_RANK), default="medium", help="highest live risk approved by the human operator")
    heal_parser.set_defaults(handler=command_heal)

    reconcile_parser = subparsers.add_parser("reconcile", help="retry old-key revocations left pending")
    reconcile_parser.add_argument("--execute", action="store_true")
    reconcile_parser.add_argument("--ack-keep-access", action="store_true")
    reconcile_parser.add_argument("--approve-risk", choices=tuple(RISK_RANK), default="medium")
    reconcile_parser.set_defaults(handler=command_reconcile)

    watch_parser = subparsers.add_parser("watch", help="continuously scan and optionally auto-heal eligible credentials")
    watch_parser.add_argument("--git-history", action="store_true")
    watch_parser.add_argument("--execute", action="store_true")
    watch_parser.add_argument("--ack-keep-access", action="store_true")
    watch_parser.add_argument("--interval", type=int, default=300)
    watch_parser.add_argument("--max-cycles", type=int, default=0, help="zero means run until stopped")
    watch_parser.set_defaults(handler=command_watch)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "connectors":
            return int(args.handler(args, None))
        settings = load_config(Path(args.config))
        return int(args.handler(args, settings))
    except (ConfigError, RotationBusy, ScanIncomplete, ValueError) as exc:
        _print({"status": "blocked", "error": str(exc)}, as_json=getattr(args, "json", False))
        return EXIT_BLOCKED
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
