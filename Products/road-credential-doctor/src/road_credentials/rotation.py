from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Iterable

from .models import Credential, Finding, Settings
from .policy import risk_allows
from .receipts import utc_now, write_receipt
from .runner import ConnectorResult, dispatch_connector
from .state import atomic_write_json, load_state, rotation_lock


class RotationError(RuntimeError):
    pass


@dataclass(frozen=True)
class RotationOutcome:
    credential_id: str
    rotation_id: str
    status: str
    access_retained: bool
    old_revoked: bool
    receipt_path: str | None
    message: str

    def public(self) -> dict[str, Any]:
        return {
            "credential_id": self.credential_id,
            "rotation_id": self.rotation_id,
            "status": self.status,
            "access_retained": self.access_retained,
            "old_revoked": self.old_revoked,
            "receipt_path": self.receipt_path,
            "message": self.message,
        }


def _event(
    events: list[dict[str, Any]],
    phase: str,
    result: ConnectorResult,
    consumer_id: str | None = None,
) -> None:
    event: dict[str, Any] = {
        "phase": phase,
        "outcome": "ok" if result.ok else "failed",
        "returncode": result.returncode,
        "duration_ms": result.duration_ms,
        "connector_execution_id": result.execution_id,
    }
    if consumer_id:
        event["consumer_id"] = consumer_id
    events.append(event)


def _run(
    settings: Settings,
    credential: Credential,
    action: str,
    rotation_id: str,
    phase: str,
    events: list[dict[str, Any]],
    *,
    old_provider_id: str,
    new_provider_id: str = "",
    approved_risk: str,
    consumer_id: str | None = None,
) -> ConnectorResult:
    request = {
        "schema_version": 1,
        "connector_runtime_id": settings.connector_runtime_id,
        "connector": credential.connector,
        "credential_id": credential.id,
        "rotation_id": rotation_id,
        "phase": phase,
        "action": action,
        "risk": credential.risk,
        "approved_risk": approved_risk,
        "old_provider_id": old_provider_id or None,
        "new_provider_id": new_provider_id or None,
        "consumer_id": consumer_id,
    }
    result = dispatch_connector(
        settings.connector_dispatch,
        cwd=settings.config_path.parent,
        connector_runtime_id=settings.connector_runtime_id,
        request=request,
    )
    _event(events, phase, result, consumer_id)
    return result


def _rollback(
    settings: Settings,
    credential: Credential,
    rotation_id: str,
    updated_ids: list[str],
    old_provider_id: str,
    new_provider_id: str,
    events: list[dict[str, Any]],
    approved_risk: str,
    activation_attempted: bool,
    create_attempted: bool,
) -> bool:
    consumers = {consumer.id: consumer for consumer in credential.consumers}
    rollback_ok = True
    for consumer_id in reversed(updated_ids):
        consumer = consumers[consumer_id]
        result = _run(
            settings,
            credential,
            consumer.rollback_action,
            rotation_id,
            "rollback_consumer",
            events,
            old_provider_id=old_provider_id,
            new_provider_id=new_provider_id,
            approved_risk=approved_risk,
            consumer_id=consumer_id,
        )
        rollback_ok = rollback_ok and result.ok
    if activation_attempted:
        result = _run(
            settings,
            credential,
            credential.restore_action,
            rotation_id,
            "restore_connector_active_version",
            events,
            old_provider_id=old_provider_id,
            new_provider_id=new_provider_id,
            approved_risk=approved_risk,
        )
        rollback_ok = rollback_ok and result.ok
    if rollback_ok and create_attempted:
        result = _run(
            settings,
            credential,
            credential.revoke_new_action,
            rotation_id,
            "revoke_unused_replacement",
            events,
            old_provider_id=old_provider_id,
            new_provider_id=new_provider_id,
            approved_risk=approved_risk,
        )
        rollback_ok = rollback_ok and result.ok
    return rollback_ok


def _finalize(settings: Settings, state: dict[str, Any], receipt: dict[str, Any]) -> str:
    path, receipt_hash = write_receipt(
        settings.receipt_dir,
        receipt,
        previous_hash=state.get("last_receipt_hash"),
    )
    state["last_receipt_hash"] = receipt_hash
    atomic_write_json(settings.state_file, state)
    return str(path)


def rotate(
    settings: Settings,
    credential: Credential,
    findings: Iterable[Finding],
    *,
    approved_risk: str,
) -> RotationOutcome:
    if not credential.consumers:
        raise ValueError("rotation requires at least one declared consumer")
    if not risk_allows(credential.risk, approved_risk):
        raise ValueError(f"{credential.id} risk {credential.risk} exceeds approval {approved_risk}")
    if credential.risk in {"high", "critical"} and credential.authorize_action is None:
        raise ValueError(f"{credential.id} requires a connector authorization action")
    rotation_id = uuid.uuid4().hex[:16]
    started_at = utc_now()
    finding_list = list(findings)
    events: list[dict[str, Any]] = []
    updated_ids: list[str] = []
    old_revoked = False
    activation_attempted = False
    create_attempted = False

    with rotation_lock(settings.state_file):
        state = load_state(settings.state_file)
        if any(item.get("credential_id") == credential.id for item in state.get("pending_revocations", [])):
            raise ValueError("reconcile pending revocation before another rotation")
        active = state.setdefault("active", {}).get(credential.id, {})
        old_provider_id = str(active.get("provider_id") or credential.provider_id or "")
        if not old_provider_id.strip():
            raise ValueError("rotation requires a non-empty old provider id")
        new_provider_id = ""
        status = "failed_access_retained"
        message = "connector rotation failed before revocation; the old provider credential remains active"
        access_retained = True
        try:
            if credential.authorize_action is not None:
                authorized = _run(
                    settings,
                    credential,
                    credential.authorize_action,
                    rotation_id,
                    "authorize_rotation",
                    events,
                    old_provider_id=old_provider_id,
                    approved_risk=approved_risk,
                )
                if not authorized.ok:
                    raise RotationError("connector authorization was denied")

            for consumer in credential.consumers:
                baseline = _run(
                    settings,
                    credential,
                    consumer.verify_action,
                    rotation_id,
                    "baseline_consumer",
                    events,
                    old_provider_id=old_provider_id,
                    approved_risk=approved_risk,
                    consumer_id=consumer.id,
                )
                if not baseline.ok:
                    raise RotationError(f"consumer baseline is already unhealthy: {consumer.id}")

            create_attempted = True
            created = _run(
                settings,
                credential,
                credential.create_action,
                rotation_id,
                "create_new",
                events,
                old_provider_id=old_provider_id,
                approved_risk=approved_risk,
            )
            if not created.ok or not created.provider_id:
                raise RotationError("connector could not create a replacement provider credential")
            candidate_provider_id = created.provider_id
            if candidate_provider_id == old_provider_id:
                raise RotationError("connector returned the old provider id as the replacement")
            new_provider_id = candidate_provider_id

            validated = _run(
                settings,
                credential,
                credential.validate_action,
                rotation_id,
                "validate_new",
                events,
                old_provider_id=old_provider_id,
                new_provider_id=new_provider_id,
                approved_risk=approved_risk,
            )
            if not validated.ok:
                raise RotationError("connector did not validate the replacement")

            for consumer in credential.consumers:
                updated_ids.append(consumer.id)
                updated = _run(
                    settings,
                    credential,
                    consumer.update_action,
                    rotation_id,
                    "update_consumer",
                    events,
                    old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id,
                    approved_risk=approved_risk,
                    consumer_id=consumer.id,
                )
                if not updated.ok:
                    raise RotationError(f"connector consumer update failed: {consumer.id}")
                verified = _run(
                    settings,
                    credential,
                    consumer.verify_action,
                    rotation_id,
                    "verify_consumer",
                    events,
                    old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id,
                    approved_risk=approved_risk,
                    consumer_id=consumer.id,
                )
                if not verified.ok:
                    raise RotationError(f"connector consumer verification failed: {consumer.id}")

            activation_attempted = True
            activated = _run(
                settings,
                credential,
                credential.activate_action,
                rotation_id,
                "activate_connector_version",
                events,
                old_provider_id=old_provider_id,
                new_provider_id=new_provider_id,
                approved_risk=approved_risk,
            )
            if not activated.ok:
                raise RotationError("connector could not activate the replacement")

            pending = {
                "credential_id": credential.id,
                "rotation_id": rotation_id,
                "provider_id": old_provider_id,
                "fingerprints": sorted({finding.fingerprint for finding in finding_list}),
                "created_at": utc_now(),
            }
            state.setdefault("pending_revocations", []).append(pending)
            state.setdefault("active", {})[credential.id] = {
                "provider_id": new_provider_id,
                "last_rotation_id": rotation_id,
                "updated_at": utc_now(),
            }
            atomic_write_json(settings.state_file, state)

            revoked = _run(
                settings,
                credential,
                credential.revoke_old_action,
                rotation_id,
                "revoke_old",
                events,
                old_provider_id=old_provider_id,
                new_provider_id=new_provider_id,
                approved_risk=approved_risk,
            )
            if revoked.ok:
                old_revoked = True
                status = "rotated"
                message = "connector verified every consumer and revoked the old provider credential"
                state["pending_revocations"] = [
                    item for item in state.get("pending_revocations", []) if item.get("rotation_id") != rotation_id
                ]
                retired = set(state.get("retired_fingerprints", []))
                retired.update(finding.fingerprint for finding in finding_list)
                state["retired_fingerprints"] = sorted(retired)
            else:
                status = "pending_revocation"
                message = "connector replacement is active; connector must retry old-key revocation"
        except RotationError as exc:
            rollback_ok = _rollback(
                settings,
                credential,
                rotation_id,
                updated_ids,
                old_provider_id,
                new_provider_id,
                events,
                approved_risk,
                activation_attempted,
                create_attempted,
            )
            access_retained = rollback_ok
            status = "failed_rolled_back" if rollback_ok else "failed_access_retained"
            message = (
                f"{exc}; connector restored the prior provider version"
                if rollback_ok
                else f"{exc}; old key was not revoked, but connector rollback needs intervention"
            )

        receipt = {
            "schema_version": 2,
            "rotation_id": rotation_id,
            "credential_id": credential.id,
            "connector_runtime_id": settings.connector_runtime_id,
            "connector": credential.connector,
            "risk": credential.risk,
            "approval": {"approved_through": approved_risk},
            "started_at": started_at,
            "completed_at": utc_now(),
            "status": status,
            "access_retained": access_retained,
            "old_revoked": old_revoked,
            "finding_fingerprints": sorted({finding.fingerprint for finding in finding_list}),
            "events": events,
        }
        receipt_path = _finalize(settings, state, receipt)
        return RotationOutcome(
            credential_id=credential.id,
            rotation_id=rotation_id,
            status=status,
            access_retained=access_retained,
            old_revoked=old_revoked,
            receipt_path=receipt_path,
            message=message,
        )


def reconcile_pending(
    settings: Settings,
    credential: Credential,
    *,
    approved_risk: str,
) -> list[RotationOutcome]:
    if not risk_allows(credential.risk, approved_risk):
        raise ValueError(f"{credential.id} risk {credential.risk} exceeds approval {approved_risk}")
    if credential.risk in {"high", "critical"} and credential.authorize_action is None:
        raise ValueError(f"{credential.id} requires a connector authorization action")
    outcomes: list[RotationOutcome] = []
    with rotation_lock(settings.state_file):
        state = load_state(settings.state_file)
        pending_items = [
            item for item in state.get("pending_revocations", []) if item.get("credential_id") == credential.id
        ]
        for item in pending_items:
            rotation_id = str(item.get("rotation_id") or uuid.uuid4().hex[:16])
            old_provider_id = str(item.get("provider_id") or "")
            events: list[dict[str, Any]] = []
            authorized = True
            if credential.authorize_action is not None:
                approval = _run(
                    settings,
                    credential,
                    credential.authorize_action,
                    rotation_id,
                    "authorize_revocation_retry",
                    events,
                    old_provider_id=old_provider_id,
                    approved_risk=approved_risk,
                )
                authorized = approval.ok
            result = (
                _run(
                    settings,
                    credential,
                    credential.revoke_old_action,
                    rotation_id,
                    "retry_revoke_old",
                    events,
                    old_provider_id=old_provider_id,
                    approved_risk=approved_risk,
                )
                if authorized
                else ConnectorResult(False, 77, 0)
            )
            if result.ok:
                state["pending_revocations"].remove(item)
                retired = set(state.get("retired_fingerprints", []))
                retired.update(item.get("fingerprints", []))
                state["retired_fingerprints"] = sorted(retired)
                status = "revocation_reconciled"
                message = "connector completed pending old-key revocation"
            else:
                status = "pending_revocation"
                message = "old credential remains active; connector retry failed safely"
            receipt = {
                "schema_version": 2,
                "rotation_id": rotation_id,
                "credential_id": credential.id,
                "connector_runtime_id": settings.connector_runtime_id,
                "connector": credential.connector,
                "risk": credential.risk,
                "approval": {"approved_through": approved_risk},
                "started_at": utc_now(),
                "completed_at": utc_now(),
                "status": status,
                "access_retained": True,
                "old_revoked": result.ok,
                "finding_fingerprints": list(item.get("fingerprints", [])),
                "events": events,
            }
            receipt_path = _finalize(settings, state, receipt)
            outcomes.append(
                RotationOutcome(
                    credential_id=credential.id,
                    rotation_id=rotation_id,
                    status=status,
                    access_retained=True,
                    old_revoked=result.ok,
                    receipt_path=receipt_path,
                    message=message,
                )
            )
    return outcomes
