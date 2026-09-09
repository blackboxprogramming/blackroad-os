from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .state import atomic_write_json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_receipt(
    receipt_dir: Path,
    receipt: dict[str, Any],
    *,
    previous_hash: str | None,
) -> tuple[Path, str]:
    payload = dict(receipt)
    payload["previous_receipt_hash"] = previous_hash
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt_hash = "sha256:" + hashlib.sha256(canonical).hexdigest()
    payload["receipt_hash"] = receipt_hash
    stamp = payload["started_at"].replace(":", "").replace("-", "").replace(".", "")
    path = receipt_dir / f"{stamp}_{payload['rotation_id']}.json"
    atomic_write_json(path, payload)
    return path, receipt_hash

