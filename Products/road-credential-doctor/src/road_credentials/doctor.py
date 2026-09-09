from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .catalog import known_user_connector_ids
from .models import CommandSpec, Credential, Settings
from .scanner import looks_like_secret
from .state import load_state


VALID_RISKS = {"low", "medium", "high", "critical"}
ACTION_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,255}$")


@dataclass(frozen=True)
class Check:
    level: str
    code: str
    message: str

    def public(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


def _command_checks(settings: Settings, owner: str, spec: CommandSpec) -> list[Check]:
    checks: list[Check] = []
    joined = " ".join(spec.argv)
    forbidden = ("{{secret}}", "${SECRET}", "$SECRET", "%SECRET%", "ROAD_SECRET_VALUE")
    if looks_like_secret(joined) or any(marker in joined for marker in forbidden):
        checks.append(Check("error", "SECRET_IN_COMMAND", f"{owner} contains secret material or interpolation"))
    program = spec.argv[0]
    if "/" in program:
        candidate = Path(program)
        if not candidate.is_absolute():
            candidate = settings.config_path.parent / candidate
        available = candidate.is_file() and os.access(candidate, os.X_OK)
    else:
        available = shutil.which(program) is not None
    if not available:
        checks.append(Check("error", "COMMAND_NOT_FOUND", f"{owner} program is unavailable: {program}"))
    return checks


def _all_actions(credential: Credential):
    if credential.authorize_action:
        yield "authorize", credential.authorize_action
    yield "create", credential.create_action
    yield "validate", credential.validate_action
    yield "activate", credential.activate_action
    yield "restore", credential.restore_action
    yield "revoke_old", credential.revoke_old_action
    yield "revoke_new", credential.revoke_new_action
    for consumer in credential.consumers:
        yield f"consumer {consumer.id} update", consumer.update_action
        yield f"consumer {consumer.id} verify", consumer.verify_action
        yield f"consumer {consumer.id} rollback", consumer.rollback_action


def _receipt_checks(settings: Settings) -> list[Check]:
    checks: list[Check] = []
    previous: str | None = None
    receipt_files = sorted(settings.receipt_dir.glob("*.json")) if settings.receipt_dir.is_dir() else []
    for path in receipt_files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            claimed = payload.pop("receipt_hash")
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            calculated = "sha256:" + hashlib.sha256(canonical).hexdigest()
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            checks.append(Check("error", "RECEIPT_INVALID", f"receipt is unreadable or malformed: {path.name}"))
            continue
        if claimed != calculated:
            checks.append(Check("error", "RECEIPT_TAMPERED", f"receipt hash does not match: {path.name}"))
        if payload.get("previous_receipt_hash") != previous:
            checks.append(Check("error", "RECEIPT_CHAIN_BROKEN", f"receipt chain is broken at: {path.name}"))
        previous = claimed
    state_hash = load_state(settings.state_file).get("last_receipt_hash")
    if state_hash != previous:
        checks.append(Check("error", "STATE_RECEIPT_MISMATCH", "state does not point to the latest receipt"))
    return checks


def run_doctor(settings: Settings, *, repair: bool = False) -> list[Check]:
    checks: list[Check] = []
    if not settings.root.is_dir():
        checks.append(Check("error", "ROOT_MISSING", f"scan root does not exist: {settings.root}"))
    if not settings.credentials:
        checks.append(Check("warning", "NO_CREDENTIALS", "no credential lifecycles are configured"))
    if repair:
        settings.state_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        settings.receipt_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(settings.state_file.parent, 0o700)
        os.chmod(settings.receipt_dir, 0o700)
        if settings.state_file.exists():
            os.chmod(settings.state_file, 0o600)
    for path, label in (
        (settings.state_file.parent, "state directory"),
        (settings.receipt_dir, "receipt directory"),
    ):
        if path.exists() and path.stat().st_mode & 0o077:
            checks.append(Check("error", "INSECURE_RUNTIME_PERMISSIONS", f"{label} must not allow group or other access: {path}"))
    if settings.state_file.exists() and settings.state_file.stat().st_mode & 0o077:
        checks.append(Check("error", "INSECURE_STATE_PERMISSIONS", f"state file must be owner-only: {settings.state_file}"))
    checks.extend(_receipt_checks(settings))
    checks.extend(_command_checks(settings, "connector runtime dispatch", settings.connector_dispatch))
    state = load_state(settings.state_file)
    for pending in state.get("pending_revocations", []):
        if not pending.get("provider_id"):
            checks.append(
                Check(
                    "error",
                    "PENDING_PROVIDER_ID_MISSING",
                    f"pending revocation lacks a durable provider id for {pending.get('credential_id', 'unknown')}",
                )
            )
    name_owners: dict[str, list[str]] = {}
    for credential in settings.credentials:
        if credential.connector not in known_user_connector_ids():
            checks.append(Check("error", "UNKNOWN_CONNECTOR", f"{credential.id} uses unknown connector: {credential.connector}"))
        for name in credential.names:
            name_owners.setdefault(name, []).append(credential.id)
    for name, owners in name_owners.items():
        if len(owners) > 1:
            checks.append(Check("error", "AMBIGUOUS_SECRET_NAME", f"{name} is owned by multiple credentials: {', '.join(owners)}"))
    for credential in settings.credentials:
        if credential.risk not in VALID_RISKS:
            checks.append(Check("error", "INVALID_RISK", f"{credential.id} risk must be low, medium, high, or critical"))
        if not credential.kinds and not credential.fingerprints:
            checks.append(Check("error", "UNBOUNDED_MATCH", f"{credential.id} must match a kind or fingerprint"))
        if not credential.names:
            checks.append(Check("error", "NO_SECRET_NAMES", f"{credential.id} cannot prove consumer coverage without secret names"))
        if credential.auto_heal and credential.risk in {"high", "critical"}:
            checks.append(Check("error", "AUTO_HEAL_RISK", f"{credential.id} is {credential.risk} risk and requires human approval"))
        if credential.risk in {"high", "critical"} and credential.authorize_action is None:
            checks.append(Check("error", "AUTHORIZATION_ACTION_REQUIRED", f"{credential.id} requires a high-risk connector authorization action"))
        if credential.auto_heal and not credential.consumers:
            checks.append(Check("error", "AUTO_HEAL_NO_CONSUMERS", f"{credential.id} cannot auto-heal without a verified consumer"))
        for consumer in credential.consumers:
            if not consumer.paths:
                checks.append(Check("error", "UNBOUNDED_CONSUMER", f"{credential.id}/{consumer.id} must declare covered paths or external locators"))
        if credential.provider_id is None:
            checks.append(Check("error", "NO_PROVIDER_ID", f"{credential.id} cannot durably retry first-run revocation after a process crash"))
        for name, action in _all_actions(credential):
            if not ACTION_NAME.fullmatch(action):
                checks.append(Check("error", "INVALID_CONNECTOR_ACTION", f"{credential.id} {name} is not a valid connector action name"))
    if not checks:
        checks.append(Check("ok", "READY", "configuration and connector transport are ready"))
    return checks
