from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import CommandSpec, Consumer, Credential, Settings


class ConfigError(ValueError):
    pass


ACTION_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,255}$")


def _command(value: Any, location: str, *, required: bool = True) -> CommandSpec | None:
    if value is None and not required:
        return None
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise ConfigError(f"{location} must be a non-empty JSON array of strings")
    return CommandSpec(tuple(value))


def _strings(value: Any, location: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise ConfigError(f"{location} must be a JSON array of non-empty strings")
    return tuple(value)


def _action(value: Any, location: str, *, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or not ACTION_NAME.fullmatch(value):
        raise ConfigError(f"{location} must be a non-empty connector action name")
    return value


def load_config(path: str | Path) -> Settings:
    config_path = Path(path).expanduser().resolve()
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"configuration not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc

    if raw.get("schema_version") != 3:
        raise ConfigError("schema_version must be 3")
    base = config_path.parent
    root = (base / raw.get("root", ".")).resolve()
    runtime = raw.get("runtime", {})
    state_file = (base / runtime.get("state_file", ".road-credentials/state.json")).resolve()
    receipt_dir = (base / runtime.get("receipt_dir", ".road-credentials/receipts")).resolve()
    scan = raw.get("scan", {})
    ignore_file = (root / scan.get("ignore_file", ".roadcredentialsignore")).resolve()
    connector_runtime = raw.get("connector_runtime", {})
    connector_runtime_id = connector_runtime.get("id")
    if not isinstance(connector_runtime_id, str) or not connector_runtime_id:
        raise ConfigError("connector_runtime.id must be a non-empty connector-host identity")
    if connector_runtime.get("transport") != "connector_rpc":
        raise ConfigError("connector_runtime.transport must be connector_rpc")
    connector_dispatch = _command(connector_runtime.get("dispatch"), "connector_runtime.dispatch")

    credentials: list[Credential] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw.get("credentials", [])):
        where = f"credentials[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{where} must be an object")
        credential_id = item.get("id")
        if not isinstance(credential_id, str) or not credential_id:
            raise ConfigError(f"{where}.id must be a non-empty string")
        if credential_id in seen_ids:
            raise ConfigError(f"duplicate credential id: {credential_id}")
        seen_ids.add(credential_id)
        detect = item.get("detect", {})
        lifecycle = item.get("lifecycle", {})
        consumers: list[Consumer] = []
        consumer_ids: set[str] = set()
        for c_index, consumer in enumerate(item.get("consumers", [])):
            c_where = f"{where}.consumers[{c_index}]"
            consumer_id = consumer.get("id") if isinstance(consumer, dict) else None
            if not isinstance(consumer_id, str) or not consumer_id:
                raise ConfigError(f"{c_where}.id must be a non-empty string")
            if consumer_id in consumer_ids:
                raise ConfigError(f"duplicate consumer id in {credential_id}: {consumer_id}")
            consumer_ids.add(consumer_id)
            consumers.append(
                Consumer(
                    id=consumer_id,
                    paths=_strings(consumer.get("paths"), f"{c_where}.paths"),
                    update_action=_action(consumer.get("update_action"), f"{c_where}.update_action"),
                    verify_action=_action(consumer.get("verify_action"), f"{c_where}.verify_action"),
                    rollback_action=_action(consumer.get("rollback_action"), f"{c_where}.rollback_action"),
                )
            )
        credentials.append(
            Credential(
                id=credential_id,
                connector=str(item.get("connector", "custom")),
                risk=str(item.get("risk", "high")),
                provider_id=item.get("provider_id") if isinstance(item.get("provider_id"), str) else None,
                kinds=_strings(detect.get("kinds"), f"{where}.detect.kinds"),
                names=_strings(detect.get("names"), f"{where}.detect.names"),
                paths=_strings(detect.get("paths"), f"{where}.detect.paths"),
                fingerprints=_strings(detect.get("fingerprints"), f"{where}.detect.fingerprints"),
                auto_heal=bool(item.get("auto_heal", False)),
                authorize_action=_action(lifecycle.get("authorize_action"), f"{where}.lifecycle.authorize_action", required=False),
                create_action=_action(lifecycle.get("create_action"), f"{where}.lifecycle.create_action"),
                validate_action=_action(lifecycle.get("validate_action"), f"{where}.lifecycle.validate_action"),
                activate_action=_action(lifecycle.get("activate_action"), f"{where}.lifecycle.activate_action"),
                restore_action=_action(lifecycle.get("restore_action"), f"{where}.lifecycle.restore_action"),
                revoke_old_action=_action(lifecycle.get("revoke_old_action"), f"{where}.lifecycle.revoke_old_action"),
                revoke_new_action=_action(lifecycle.get("revoke_new_action"), f"{where}.lifecycle.revoke_new_action"),
                consumers=tuple(consumers),
            )
        )

    return Settings(
        config_path=config_path,
        root=root,
        state_file=state_file,
        receipt_dir=receipt_dir,
        ignore_file=ignore_file,
        max_file_bytes=int(scan.get("max_file_bytes", 2_000_000)),
        history_max_bytes=int(scan.get("history_max_bytes", 25_000_000)),
        reference_ignore_paths=_strings(scan.get("reference_ignore_paths"), "scan.reference_ignore_paths"),
        connector_runtime_id=connector_runtime_id,
        connector_dispatch=connector_dispatch,
        credentials=tuple(credentials),
    )
