from __future__ import annotations

import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class RotationBusy(RuntimeError):
    pass


OPERATION_STAGES = {
    "create_pending",
    "created",
    "validated",
    "updating_consumers",
    "activated",
}
MAX_STATE_BYTES = 4 * 1024 * 1024
ROTATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field in state: {key}")
        result[key] = value
    return result


def _string(value: Any, location: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} must be a non-empty string")


def _string_list(value: Any, location: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{location} must be an array of non-empty strings")


def _exact_fields(
    value: Any,
    location: str,
    required: set[str],
    optional: set[str] | frozenset[str] = frozenset(),
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{location} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing:
        raise ValueError(f"{location} is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"{location} has unknown fields: {', '.join(sorted(unknown))}")
    return value


def _validate_execution_binding(item: dict[str, Any], location: str) -> None:
    # Legacy records remain readable, but cannot be automatically replayed.
    if "execution_config_hash" in item:
        value = item["execution_config_hash"]
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"{location}.execution_config_hash must be a SHA-256 hex digest")


def validate_state(data: Any, path: Path | None = None) -> dict[str, Any]:
    location = str(path) if path else "state"
    root = _exact_fields(
        data,
        location,
        {"schema_version"},
        {"active", "pending_operations", "pending_revocations", "retired_fingerprints", "last_receipt_hash"},
    )
    if root.get("schema_version") != 1:
        raise ValueError(f"unsupported state schema in {location}")

    active = root.get("active", {})
    if not isinstance(active, dict):
        raise ValueError(f"{location}.active must be an object")
    for credential_id, value in active.items():
        _string(credential_id, f"{location}.active credential id")
        item = _exact_fields(
            value,
            f"{location}.active[{credential_id!r}]",
            {"provider_id", "last_rotation_id", "updated_at"},
        )
        for field in ("provider_id", "last_rotation_id", "updated_at"):
            _string(item.get(field), f"{location}.active[{credential_id!r}].{field}")

    operations = root.get("pending_operations", [])
    if not isinstance(operations, list):
        raise ValueError(f"{location}.pending_operations must be an array")
    operation_ids: set[str] = set()
    for index, value in enumerate(operations):
        item_location = f"{location}.pending_operations[{index}]"
        item = _exact_fields(
            value,
            item_location,
            {
                "credential_id", "connector", "rotation_id", "stage", "old_provider_id",
                "new_provider_id", "updated_consumers", "fingerprints", "created_at", "updated_at",
            },
            {"last_error", "execution_config_hash"},
        )
        _validate_execution_binding(item, item_location)
        for field in ("credential_id", "connector", "rotation_id", "old_provider_id", "created_at", "updated_at"):
            _string(item.get(field), f"{item_location}.{field}")
        if not ROTATION_ID.fullmatch(item["rotation_id"]):
            raise ValueError(f"{item_location}.rotation_id contains unsafe characters")
        _string(item.get("new_provider_id"), f"{item_location}.new_provider_id", optional=True)
        if item.get("stage") not in OPERATION_STAGES:
            raise ValueError(f"{item_location}.stage is not supported")
        if item["stage"] == "create_pending" and item.get("new_provider_id") is not None:
            raise ValueError(f"{item_location}.new_provider_id must be null before creation is proven")
        if item["stage"] != "create_pending" and not item.get("new_provider_id"):
            raise ValueError(f"{item_location}.new_provider_id is required after creation")
        if item.get("new_provider_id") == item.get("old_provider_id"):
            raise ValueError(f"{item_location} replacement must differ from the old provider id")
        _string_list(item.get("updated_consumers"), f"{item_location}.updated_consumers")
        _string_list(item.get("fingerprints"), f"{item_location}.fingerprints")
        if "last_error" in item:
            _string(item.get("last_error"), f"{item_location}.last_error")
        if item["rotation_id"] in operation_ids:
            raise ValueError(f"duplicate pending operation rotation id: {item['rotation_id']}")
        operation_ids.add(item["rotation_id"])

    revocations = root.get("pending_revocations", [])
    if not isinstance(revocations, list):
        raise ValueError(f"{location}.pending_revocations must be an array")
    revocation_ids: set[str] = set()
    for index, value in enumerate(revocations):
        item_location = f"{location}.pending_revocations[{index}]"
        item = _exact_fields(
            value,
            item_location,
            {"credential_id", "rotation_id", "provider_id", "fingerprints", "created_at"},
            {"execution_config_hash"},
        )
        _validate_execution_binding(item, item_location)
        for field in ("credential_id", "rotation_id", "provider_id", "created_at"):
            _string(item.get(field), f"{item_location}.{field}")
        if not ROTATION_ID.fullmatch(item["rotation_id"]):
            raise ValueError(f"{item_location}.rotation_id contains unsafe characters")
        _string_list(item.get("fingerprints"), f"{item_location}.fingerprints")
        if item["rotation_id"] in revocation_ids:
            raise ValueError(f"duplicate pending revocation rotation id: {item['rotation_id']}")
        revocation_ids.add(item["rotation_id"])
    overlap = operation_ids & revocation_ids
    if overlap:
        raise ValueError(f"rotation cannot be operation-pending and revocation-pending: {sorted(overlap)[0]}")

    _string_list(root.get("retired_fingerprints", []), f"{location}.retired_fingerprints")
    receipt_hash = root.get("last_receipt_hash")
    if receipt_hash is not None:
        _string(receipt_hash, f"{location}.last_receipt_hash")
    return root


def empty_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "active": {},
        "pending_operations": [],
        "pending_revocations": [],
        "retired_fingerprints": [],
        "last_receipt_hash": None,
    }


def load_state(path: Path) -> dict[str, Any]:
    try:
        if path.stat().st_size > MAX_STATE_BYTES:
            raise ValueError(f"state exceeds {MAX_STATE_BYTES} bytes: {path}")
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except FileNotFoundError:
        return empty_state()
    except UnicodeDecodeError as exc:
        raise ValueError(f"state is not valid UTF-8: {path}") from exc
    except RecursionError as exc:
        raise ValueError(f"state JSON nesting is too deep: {path}") from exc
    except OSError as exc:
        raise ValueError(f"state could not be read: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"state must be an object: {path}")
    base = empty_state()
    base.update(data)
    return validate_state(base, path)


def atomic_write_json(path: Path, data: dict[str, Any], *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary_path.unlink(missing_ok=True)


@contextmanager
def rotation_lock(state_path: Path) -> Iterator[None]:
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RotationBusy("another credential rotation is already running") from exc
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)
