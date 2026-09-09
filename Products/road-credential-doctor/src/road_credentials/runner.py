from __future__ import annotations

import os
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .models import CommandSpec


SAFE_ENVIRONMENT_NAMES = {
    "HOME",
    "LANG",
    "LOGNAME",
    "PATH",
    "SHELL",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TMPDIR",
    "USER",
    "XDG_CACHE_HOME",
    "XDG_CONFIG_HOME",
}
ALLOWED_RESPONSE_FIELDS = {"ok", "execution_id", "authority", "secret_material", "provider_id"}


@dataclass(frozen=True)
class ConnectorResult:
    ok: bool
    returncode: int
    duration_ms: int
    execution_id: str | None = None
    provider_id: str | None = None


def dispatch_connector(
    spec: CommandSpec,
    *,
    cwd: Path,
    connector_runtime_id: str,
    request: Mapping[str, Any],
) -> ConnectorResult:
    """Dispatch metadata to a connector host. Credential bytes are never accepted."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if key in SAFE_ENVIRONMENT_NAMES or key.startswith("LC_")
    }
    environment.update(
        {
            "ROAD_CONNECTOR_RUNTIME_ID": connector_runtime_id,
            "ROAD_CONNECTOR_TRANSPORT": "connector_rpc",
        }
    )
    payload = json.dumps(dict(request), sort_keys=True, separators=(",", ":")).encode("utf-8")
    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(spec.argv),
            cwd=cwd,
            env=environment,
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=spec.timeout_seconds,
            check=False,
        )
        duration_ms = round((time.monotonic() - started) * 1000)
        if completed.returncode != 0 or len(completed.stdout) > 65536:
            return ConnectorResult(False, completed.returncode or 65, duration_ms)
        try:
            response = json.loads(completed.stdout.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return ConnectorResult(False, 65, duration_ms)
        if not isinstance(response, dict) or set(response) - ALLOWED_RESPONSE_FIELDS:
            return ConnectorResult(False, 65, duration_ms)
        execution_id = response.get("execution_id")
        provider_id = response.get("provider_id")
        valid = (
            isinstance(response.get("ok"), bool)
            and response.get("authority") == "connector"
            and response.get("secret_material") is False
            and isinstance(execution_id, str)
            and 0 < len(execution_id) <= 1024
            and (provider_id is None or isinstance(provider_id, str) and 0 < len(provider_id) <= 1024)
        )
        if not valid:
            return ConnectorResult(False, 65, duration_ms)
        return ConnectorResult(
            bool(response["ok"]),
            0 if response["ok"] else 1,
            duration_ms,
            execution_id=execution_id,
            provider_id=provider_id,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ConnectorResult(
            ok=False,
            returncode=124,
            duration_ms=round((time.monotonic() - started) * 1000),
        )
