from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .state import atomic_write_json


RECEIPT_ROTATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
RECEIPT_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
MAX_RECEIPT_BYTES = 16 * 1024 * 1024


class ReceiptError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError(f"duplicate receipt field: {key}")
        result[key] = value
    return result


def read_receipt(path: Path) -> dict[str, Any]:
    """Read one bounded regular receipt without following a symlink."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ReceiptError(f"receipt cannot be opened safely: {path.name}") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ReceiptError(f"receipt is not a regular file: {path.name}")
        if metadata.st_size > MAX_RECEIPT_BYTES:
            raise ReceiptError(f"receipt exceeds {MAX_RECEIPT_BYTES} bytes: {path.name}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            raw = handle.read(MAX_RECEIPT_BYTES + 1)
        if len(raw) > MAX_RECEIPT_BYTES:
            raise ReceiptError(f"receipt exceeds {MAX_RECEIPT_BYTES} bytes: {path.name}")
        try:
            payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise ReceiptError(f"receipt is not valid bounded JSON: {path.name}") from exc
        if not isinstance(payload, dict):
            raise ReceiptError(f"receipt must contain a JSON object: {path.name}")
        return payload
    finally:
        os.close(descriptor)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_receipt(
    receipt_dir: Path,
    receipt: dict[str, Any],
    *,
    previous_hash: str | None,
) -> tuple[Path, str]:
    payload = dict(receipt)
    rotation_id = payload.get("rotation_id")
    if not isinstance(rotation_id, str) or not RECEIPT_ROTATION_ID.fullmatch(rotation_id):
        raise ValueError("receipt rotation_id is not filename-safe")
    if not isinstance(payload.get("started_at"), str) or not RECEIPT_TIME.fullmatch(payload["started_at"]):
        raise ValueError("receipt started_at must be a UTC ISO-8601 timestamp")
    payload["previous_receipt_hash"] = previous_hash
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(canonical) > MAX_RECEIPT_BYTES:
        raise ValueError(f"receipt exceeds {MAX_RECEIPT_BYTES} bytes")
    receipt_hash = "sha256:" + hashlib.sha256(canonical).hexdigest()
    payload["receipt_hash"] = receipt_hash
    serialized_size = len((json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    if serialized_size > MAX_RECEIPT_BYTES:
        raise ValueError(f"receipt exceeds {MAX_RECEIPT_BYTES} bytes")
    stamp = payload["started_at"].replace(":", "").replace("-", "").replace(".", "")
    path = receipt_dir / f"{stamp}_{rotation_id}.json"
    atomic_write_json(path, payload)
    return path, receipt_hash
