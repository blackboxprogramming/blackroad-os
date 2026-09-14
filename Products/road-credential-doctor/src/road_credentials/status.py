from __future__ import annotations

from typing import Any

from .models import Settings
from .routes import rotation_route
from .state import load_state


def _route(settings: Settings, connector: str, credential_id: str, rotation_id: str) -> str:
    return rotation_route(
        runtime_id=settings.connector_runtime_id,
        connector_id=connector,
        credential_id=credential_id,
        rotation_id=rotation_id,
    )


def status_report(settings: Settings) -> dict[str, Any]:
    """Return metadata-only connector recovery status for RoadOS and Roadies."""
    state = load_state(settings.state_file)
    credentials = {credential.id: credential for credential in settings.credentials}
    issues: list[dict[str, str]] = []
    operations: list[dict[str, Any]] = []
    revocations: list[dict[str, Any]] = []

    for item in state.get("pending_operations", []):
        credential_id = item["credential_id"]
        configured = credentials.get(credential_id)
        connector = item["connector"]
        if configured is None:
            issues.append({"code": "UNCONFIGURED_CREDENTIAL", "credential_id": credential_id})
        elif configured.connector != connector:
            issues.append({"code": "CONNECTOR_MISMATCH", "credential_id": credential_id})
        operations.append(
            {
                "credential_id": credential_id,
                "connector": connector,
                "rotation_id": item["rotation_id"],
                "route": _route(settings, connector, credential_id, item["rotation_id"]),
                "stage": item["stage"],
                "verified_consumers": sorted(set(item["updated_consumers"])),
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "requires_reconciliation": True,
            }
        )

    for item in state.get("pending_revocations", []):
        credential_id = item["credential_id"]
        configured = credentials.get(credential_id)
        if configured is None:
            connector = "unconfigured"
            issues.append({"code": "UNCONFIGURED_CREDENTIAL", "credential_id": credential_id})
        else:
            connector = configured.connector
        revocations.append(
            {
                "credential_id": credential_id,
                "connector": connector,
                "rotation_id": item["rotation_id"],
                "route": _route(settings, connector, credential_id, item["rotation_id"]),
                "created_at": item["created_at"],
                "requires_reconciliation": True,
            }
        )

    operations.sort(key=lambda item: (item["created_at"], item["rotation_id"]))
    revocations.sort(key=lambda item: (item["created_at"], item["rotation_id"]))
    issues.sort(key=lambda item: (item["credential_id"], item["code"]))
    return {
        "schema_version": 1,
        "connector_runtime_id": settings.connector_runtime_id,
        "active_credentials": len(state.get("active", {})),
        "pending_operation_count": len(operations),
        "pending_revocation_count": len(revocations),
        "pending_operations": operations,
        "pending_revocations": revocations,
        "issues": issues,
        "last_receipt_hash": state.get("last_receipt_hash"),
        "work_pending": bool(operations or revocations or issues),
    }
