from __future__ import annotations

import os
import json
import selectors
import signal
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
MAX_RESPONSE_BYTES = 65536


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate response field")
        result[key] = value
    return result


def _exchange(argv, cwd, environment, payload, timeout):
    """Bound stdout while concurrently writing stdin, on POSIX connector workers."""
    if os.name != "posix" or timeout <= 0:
        return 124, b""
    deadline = time.monotonic() + timeout
    process = subprocess.Popen(
        argv, cwd=cwd, env=environment, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        start_new_session=True, bufsize=0,
    )
    output = bytearray()
    sent = 0
    try:
        with selectors.DefaultSelector() as selector:
            os.set_blocking(process.stdin.fileno(), False)
            os.set_blocking(process.stdout.fileno(), False)
            selector.register(process.stdin, selectors.EVENT_WRITE)
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return 124, b""
                for key, events in selector.select(remaining):
                    if events & selectors.EVENT_WRITE:
                        try:
                            sent += os.write(key.fd, payload[sent:sent + 4096])
                        except BlockingIOError:
                            continue
                        except BrokenPipeError:
                            sent = len(payload)
                        if sent == len(payload):
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                    else:
                        try:
                            chunk = os.read(key.fd, min(4096, MAX_RESPONSE_BYTES + 1 - len(output)))
                        except BlockingIOError:
                            continue
                        if not chunk:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                        else:
                            output.extend(chunk)
                            if len(output) > MAX_RESPONSE_BYTES:
                                return 65, b""
            return process.wait(timeout=max(0, deadline - time.monotonic())), bytes(output)
    finally:
        # Bound descendants that keep pipes open, without touching other workers.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        process.stdin.close()
        process.stdout.close()


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
        returncode, output = _exchange(list(spec.argv), cwd, environment, payload, spec.timeout_seconds)
        duration_ms = round((time.monotonic() - started) * 1000)
        if returncode != 0:
            return ConnectorResult(False, returncode, duration_ms)
        try:
            response = json.loads(output.decode("utf-8"), object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, ValueError, RecursionError):
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
            and execution_id.strip() == execution_id
            and 0 < len(execution_id) <= 1024
            and (provider_id is None or isinstance(provider_id, str) and provider_id.strip() == provider_id and 0 < len(provider_id) <= 1024)
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
