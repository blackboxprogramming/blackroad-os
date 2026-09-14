from __future__ import annotations

import re
from typing import Any, Mapping

from .policy import risk_allows
from .routes import rotation_route


class ProtocolError(ValueError):
    pass


REQUEST_FIELDS = {
    "schema_version",
    "route",
    "connector_runtime_id",
    "connector",
    "credential_id",
    "rotation_id",
    "phase",
    "action",
    "risk",
    "approved_risk",
    "old_provider_id",
    "new_provider_id",
    "consumer_id",
}

PHASES = {
    "authorize_rotation",
    "baseline_consumer",
    "create_new",
    "validate_new",
    "update_consumer",
    "verify_consumer",
    "activate_connector_version",
    "rollback_consumer",
    "restore_connector_active_version",
    "revoke_unused_replacement",
    "revoke_old",
    "authorize_revocation_retry",
    "retry_revoke_old",
    "authorize_operation_recovery",
    "recover_create_new",
    "recover_validate_new",
    "recover_update_consumer",
    "recover_verify_consumer",
    "recover_activate_connector_version",
}

CONSUMER_PHASES = {
    "baseline_consumer",
    "update_consumer",
    "verify_consumer",
    "rollback_consumer",
    "recover_update_consumer",
    "recover_verify_consumer",
}

NEW_PROVIDER_PHASES = {
    "validate_new",
    "update_consumer",
    "verify_consumer",
    "activate_connector_version",
    "rollback_consumer",
    "restore_connector_active_version",
    "revoke_old",
    "retry_revoke_old",
    "recover_validate_new",
    "recover_update_consumer",
    "recover_verify_consumer",
    "recover_activate_connector_version",
}

NO_NEW_PROVIDER_PHASES = {
    "authorize_rotation",
    "baseline_consumer",
    "create_new",
    "authorize_revocation_retry",
    "recover_create_new",
}

ACTION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
RISK_LEVELS = {"low", "medium", "high", "critical"}


def _identifier(value: Any, location: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str) or value.strip() != value or not value or len(value) > 1024:
        raise ProtocolError(f"{location} must be a trimmed non-empty string of at most 1024 characters")
    return value


def validate_request(request: Mapping[str, Any], *, connector_runtime_id: str) -> dict[str, Any]:
    """Validate and normalize a metadata-only connector request schema 2."""
    if not isinstance(request, Mapping):
        raise ProtocolError("connector request must be a mapping")
    payload = dict(request)
    missing = REQUEST_FIELDS - payload.keys()
    unknown = payload.keys() - REQUEST_FIELDS
    if missing:
        raise ProtocolError(f"connector request is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ProtocolError(f"connector request has unknown fields: {', '.join(sorted(unknown))}")
    if payload["schema_version"] != 2 or isinstance(payload["schema_version"], bool):
        raise ProtocolError("connector request schema_version must be 2")

    runtime = _identifier(payload["connector_runtime_id"], "connector_runtime_id")
    expected_runtime = _identifier(connector_runtime_id, "configured connector_runtime_id")
    if runtime != expected_runtime:
        raise ProtocolError("connector_runtime_id does not match the configured runtime")
    connector = _identifier(payload["connector"], "connector")
    credential_id = _identifier(payload["credential_id"], "credential_id")
    rotation_id = _identifier(payload["rotation_id"], "rotation_id")
    old_provider_id = _identifier(payload["old_provider_id"], "old_provider_id")
    new_provider_id = _identifier(payload["new_provider_id"], "new_provider_id", optional=True)
    consumer_id = _identifier(payload["consumer_id"], "consumer_id", optional=True)

    phase = payload["phase"]
    if not isinstance(phase, str) or phase not in PHASES:
        raise ProtocolError("connector request phase is not supported")
    action = payload["action"]
    if not isinstance(action, str) or not ACTION.fullmatch(action):
        raise ProtocolError("connector request action is invalid")
    risk = payload["risk"]
    approved_risk = payload["approved_risk"]
    if not isinstance(risk, str) or not isinstance(approved_risk, str) or risk not in RISK_LEVELS or approved_risk not in RISK_LEVELS:
        raise ProtocolError("connector request risk level is invalid")
    if not risk_allows(risk, approved_risk):
        raise ProtocolError("connector request exceeds its approved risk")

    if phase in CONSUMER_PHASES and consumer_id is None:
        raise ProtocolError(f"{phase} requires consumer_id")
    if phase not in CONSUMER_PHASES and consumer_id is not None:
        raise ProtocolError(f"{phase} must not include consumer_id")
    if phase in NEW_PROVIDER_PHASES and new_provider_id is None:
        raise ProtocolError(f"{phase} requires new_provider_id")
    if phase in NO_NEW_PROVIDER_PHASES and new_provider_id is not None:
        raise ProtocolError(f"{phase} must not include new_provider_id")
    if new_provider_id is not None and new_provider_id == old_provider_id:
        raise ProtocolError("new_provider_id must differ from old_provider_id")

    expected_route = rotation_route(
        runtime_id=runtime,
        connector_id=connector,
        credential_id=credential_id,
        rotation_id=rotation_id,
        consumer_id=consumer_id,
    )
    if payload["route"] != expected_route:
        raise ProtocolError("connector request Route does not match its identifiers")
    return payload
