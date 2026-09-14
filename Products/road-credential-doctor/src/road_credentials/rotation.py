from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Iterable

from .models import Credential, Finding, Settings
from .policy import risk_allows
from .receipts import utc_now, write_receipt
from .runner import ConnectorResult, dispatch_connector
from .routes import rotation_route
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
        "schema_version": 2,
        "route": rotation_route(
            runtime_id=settings.connector_runtime_id,
            connector_id=credential.connector,
            credential_id=credential.id,
            rotation_id=rotation_id,
            consumer_id=consumer_id,
        ),
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


def _store_operation(settings: Settings, state: dict[str, Any], operation: dict[str, Any]) -> None:
    operations = state.setdefault("pending_operations", [])
    operations[:] = [item for item in operations if item.get("rotation_id") != operation["rotation_id"]]
    operation["updated_at"] = utc_now()
    operations.append(operation)
    atomic_write_json(settings.state_file, state)


def _remove_operation(state: dict[str, Any], rotation_id: str) -> None:
    state["pending_operations"] = [
        item for item in state.get("pending_operations", []) if item.get("rotation_id") != rotation_id
    ]


def _queue_revocation(
    state: dict[str, Any],
    *,
    credential_id: str,
    rotation_id: str,
    old_provider_id: str,
    new_provider_id: str,
    fingerprints: list[str],
) -> None:
    if not any(item.get("rotation_id") == rotation_id for item in state.get("pending_revocations", [])):
        state.setdefault("pending_revocations", []).append(
            {
                "credential_id": credential_id,
                "rotation_id": rotation_id,
                "provider_id": old_provider_id,
                "fingerprints": fingerprints,
                "created_at": utc_now(),
            }
        )
    state.setdefault("active", {})[credential_id] = {
        "provider_id": new_provider_id,
        "last_rotation_id": rotation_id,
        "updated_at": utc_now(),
    }
    _remove_operation(state, rotation_id)


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
        if any(
            item.get("credential_id") == credential.id
            for key in ("pending_operations", "pending_revocations")
            for item in state.get(key, [])
        ):
            raise ValueError("reconcile pending revocation or operation before another rotation")
        active = state.setdefault("active", {}).get(credential.id, {})
        old_provider_id = str(active.get("provider_id") or credential.provider_id or "")
        if not old_provider_id.strip():
            raise ValueError("rotation requires a non-empty old provider id")
        new_provider_id = ""
        status = "failed_access_retained"
        message = "connector rotation failed before revocation; the old provider credential remains active"
        access_retained = True
        operation: dict[str, Any] | None = None
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

            operation = {
                "credential_id": credential.id,
                "connector": credential.connector,
                "rotation_id": rotation_id,
                "stage": "create_pending",
                "old_provider_id": old_provider_id,
                "new_provider_id": None,
                "updated_consumers": [],
                "fingerprints": sorted({finding.fingerprint for finding in finding_list}),
                "created_at": utc_now(),
            }
            _store_operation(settings, state, operation)
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
            operation["new_provider_id"] = new_provider_id
            operation["stage"] = "created"
            _store_operation(settings, state, operation)

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
            operation["stage"] = "validated"
            _store_operation(settings, state, operation)

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
                operation["stage"] = "updating_consumers"
                operation["updated_consumers"] = list(updated_ids)
                _store_operation(settings, state, operation)

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
            operation["stage"] = "activated"
            _store_operation(settings, state, operation)
            _queue_revocation(
                state,
                credential_id=credential.id,
                rotation_id=rotation_id,
                old_provider_id=old_provider_id,
                new_provider_id=new_provider_id,
                fingerprints=operation["fingerprints"],
            )
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
            if rollback_ok and operation is not None:
                _remove_operation(state, rotation_id)
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


def reconcile_operations(
    settings: Settings,
    credential: Credential,
    *,
    approved_risk: str,
) -> list[RotationOutcome]:
    """Resume connector operations from their last durable stage.

    Connector actions must be idempotent by rotation ID. The journal is written
    before creation and after each verified boundary, so a crash may repeat an
    action but cannot silently discard the operation.
    """
    if not credential.consumers:
        raise ValueError("operation recovery requires at least one declared consumer")
    if not risk_allows(credential.risk, approved_risk):
        raise ValueError(f"{credential.id} risk {credential.risk} exceeds approval {approved_risk}")
    if credential.risk in {"high", "critical"} and credential.authorize_action is None:
        raise ValueError(f"{credential.id} requires a connector authorization action")

    outcomes: list[RotationOutcome] = []
    with rotation_lock(settings.state_file):
        state = load_state(settings.state_file)
        operations = [
            item for item in state.get("pending_operations", [])
            if item.get("credential_id") == credential.id
        ]
        for operation in operations:
            started_at = utc_now()
            events: list[dict[str, Any]] = []
            rotation_id = str(operation.get("rotation_id") or "")
            old_provider_id = str(operation.get("old_provider_id") or "")
            new_provider_id = str(operation.get("new_provider_id") or "")
            fingerprints = [
                item for item in operation.get("fingerprints", []) if isinstance(item, str)
            ]
            status = "operation_pending"
            access_retained = False
            message = "connector operation remains pending; recovery evidence was incomplete"
            try:
                if not rotation_id.strip() or not old_provider_id.strip():
                    raise RotationError("pending operation lacks a durable rotation or old provider id")
                if operation.get("connector") != credential.connector:
                    raise RotationError("pending operation connector does not match configuration")

                if credential.authorize_action is not None:
                    authorized = _run(
                        settings,
                        credential,
                        credential.authorize_action,
                        rotation_id,
                        "authorize_operation_recovery",
                        events,
                        old_provider_id=old_provider_id,
                        new_provider_id=new_provider_id,
                        approved_risk=approved_risk,
                    )
                    if not authorized.ok:
                        raise RotationError("connector operation recovery was not authorized")

                if not new_provider_id:
                    created = _run(
                        settings,
                        credential,
                        credential.create_action,
                        rotation_id,
                        "recover_create_new",
                        events,
                        old_provider_id=old_provider_id,
                        approved_risk=approved_risk,
                    )
                    if not created.ok or not created.provider_id:
                        raise RotationError("connector could not recover replacement creation")
                    new_provider_id = created.provider_id
                    if new_provider_id == old_provider_id:
                        raise RotationError("connector recovered the old provider id as the replacement")
                    operation["new_provider_id"] = new_provider_id
                    operation["stage"] = "created"
                    _store_operation(settings, state, operation)
                if new_provider_id == old_provider_id:
                    raise RotationError("pending operation replacement matches the old provider id")

                validated = _run(
                    settings,
                    credential,
                    credential.validate_action,
                    rotation_id,
                    "recover_validate_new",
                    events,
                    old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id,
                    approved_risk=approved_risk,
                )
                if not validated.ok:
                    raise RotationError("connector could not revalidate the recovered replacement")
                operation["stage"] = "validated"
                _store_operation(settings, state, operation)

                recovered_consumers: list[str] = []
                for consumer in credential.consumers:
                    updated = _run(
                        settings,
                        credential,
                        consumer.update_action,
                        rotation_id,
                        "recover_update_consumer",
                        events,
                        old_provider_id=old_provider_id,
                        new_provider_id=new_provider_id,
                        approved_risk=approved_risk,
                        consumer_id=consumer.id,
                    )
                    if not updated.ok:
                        raise RotationError(f"connector could not recover consumer update: {consumer.id}")
                    verified = _run(
                        settings,
                        credential,
                        consumer.verify_action,
                        rotation_id,
                        "recover_verify_consumer",
                        events,
                        old_provider_id=old_provider_id,
                        new_provider_id=new_provider_id,
                        approved_risk=approved_risk,
                        consumer_id=consumer.id,
                    )
                    if not verified.ok:
                        raise RotationError(f"connector could not verify recovered consumer: {consumer.id}")
                    recovered_consumers.append(consumer.id)
                    operation["stage"] = "updating_consumers"
                    operation["updated_consumers"] = list(recovered_consumers)
                    _store_operation(settings, state, operation)

                activated = _run(
                    settings,
                    credential,
                    credential.activate_action,
                    rotation_id,
                    "recover_activate_connector_version",
                    events,
                    old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id,
                    approved_risk=approved_risk,
                )
                if not activated.ok:
                    raise RotationError("connector could not recover replacement activation")
                operation["stage"] = "activated"
                _store_operation(settings, state, operation)
                _queue_revocation(
                    state,
                    credential_id=credential.id,
                    rotation_id=rotation_id,
                    old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id,
                    fingerprints=sorted(set(fingerprints)),
                )
                atomic_write_json(settings.state_file, state)
                status = "operation_recovered"
                access_retained = True
                message = "connector operation recovered; old-key revocation is durably pending"
            except RotationError as exc:
                operation["last_error"] = str(exc)
                _store_operation(settings, state, operation)
                message = f"{exc}; connector operation remains durably pending"

            receipt = {
                "schema_version": 2,
                "rotation_id": rotation_id or "invalid-operation",
                "credential_id": credential.id,
                "connector_runtime_id": settings.connector_runtime_id,
                "connector": credential.connector,
                "risk": credential.risk,
                "approval": {"approved_through": approved_risk},
                "started_at": started_at,
                "completed_at": utc_now(),
                "status": status,
                "access_retained": access_retained,
                "old_revoked": False,
                "finding_fingerprints": sorted(set(fingerprints)),
                "events": events,
            }
            receipt_path = _finalize(settings, state, receipt)
            outcomes.append(
                RotationOutcome(
                    credential_id=credential.id,
                    rotation_id=rotation_id,
                    status=status,
                    access_retained=access_retained,
                    old_revoked=False,
                    receipt_path=receipt_path,
                    message=message,
                )
            )
    return outcomes


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
            active = state.get("active", {}).get(credential.id, {})
            new_provider_id = active.get("provider_id")
            evidence_valid = bool(
                credential.consumers
                and old_provider_id.strip()
                and isinstance(new_provider_id, str)
                and new_provider_id.strip()
                and new_provider_id != old_provider_id
                and active.get("last_rotation_id") == item.get("rotation_id")
                and item.get("rotation_id")
            )
            events: list[dict[str, Any]] = []
            authorized = evidence_valid
            access_retained = False
            if authorized and credential.authorize_action is not None:
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
            if authorized:
                validated = _run(
                    settings, credential, credential.validate_action, rotation_id,
                    "validate_new", events, old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id, approved_risk=approved_risk,
                )
                access_retained = validated.ok
                if access_retained:
                    for consumer in credential.consumers:
                        verified = _run(
                            settings, credential, consumer.verify_action, rotation_id,
                            "verify_consumer", events, old_provider_id=old_provider_id,
                            new_provider_id=new_provider_id, approved_risk=approved_risk,
                            consumer_id=consumer.id,
                        )
                        if not verified.ok:
                            access_retained = False
                            break
            result = (
                _run(
                    settings,
                    credential,
                    credential.revoke_old_action,
                    rotation_id,
                    "retry_revoke_old",
                    events,
                    old_provider_id=old_provider_id,
                    new_provider_id=new_provider_id,
                    approved_risk=approved_risk,
                )
                if authorized and access_retained
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
                message = "revocation remains pending; replacement access or revocation could not be confirmed"
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
                "access_retained": access_retained,
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
                    access_retained=access_retained,
                    old_revoked=result.ok,
                    receipt_path=receipt_path,
                    message=message,
                )
            )
    return outcomes
