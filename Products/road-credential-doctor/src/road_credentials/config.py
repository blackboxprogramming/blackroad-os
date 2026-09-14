from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import CommandSpec, Consumer, Credential, Settings


class ConfigError(ValueError):
    pass


ACTION_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,255}$")
MAX_CONFIG_BYTES = 4 * 1024 * 1024


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _object(
    value: Any,
    location: str,
    *,
    allowed: set[str],
    required: set[str] | frozenset[str] = frozenset(),
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{location} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing:
        raise ConfigError(f"{location} is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ConfigError(f"{location} has unknown fields: {', '.join(sorted(unknown))}")
    return value


def _non_empty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{location} must be a non-empty string")
    return value


def _positive_int(value: Any, location: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{location} must be a positive integer")
    return value


def _command(value: Any, location: str, *, required: bool = True) -> CommandSpec | None:
    if value is None and not required:
        return None
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise ConfigError(f"{location} must be a non-empty JSON array of strings")
    return CommandSpec(tuple(value))


def _strings(value: Any, location: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
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
        if config_path.stat().st_size > MAX_CONFIG_BYTES:
            raise ConfigError(f"configuration exceeds {MAX_CONFIG_BYTES} bytes: {config_path}")
        raw = json.loads(config_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except FileNotFoundError as exc:
        raise ConfigError(f"configuration not found: {config_path}") from exc
    except UnicodeDecodeError as exc:
        raise ConfigError(f"configuration is not valid UTF-8: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    except RecursionError as exc:
        raise ConfigError("configuration JSON nesting is too deep") from exc
    except OSError as exc:
        raise ConfigError(f"configuration could not be read: {config_path}") from exc

    raw = _object(
        raw,
        "configuration",
        allowed={"schema_version", "root", "runtime", "scan", "connector_runtime", "credentials"},
        required={"schema_version", "connector_runtime", "credentials"},
    )

    if raw.get("schema_version") != 3:
        raise ConfigError("schema_version must be 3")
    base = config_path.parent
    root_value = raw.get("root", ".")
    if not isinstance(root_value, str) or not root_value:
        raise ConfigError("root must be a non-empty path string")
    root = (base / root_value).resolve()
    runtime = _object(
        raw.get("runtime", {}),
        "runtime",
        allowed={"state_file", "receipt_dir"},
    )
    for field in ("state_file", "receipt_dir"):
        if field in runtime:
            _non_empty_string(runtime[field], f"runtime.{field}")
    state_file = (base / runtime.get("state_file", ".road-credentials/state.json")).resolve()
    receipt_dir = (base / runtime.get("receipt_dir", ".road-credentials/receipts")).resolve()
    scan = _object(
        raw.get("scan", {}),
        "scan",
        allowed={"ignore_file", "max_file_bytes", "history_max_bytes", "reference_ignore_paths"},
    )
    if "ignore_file" in scan:
        _non_empty_string(scan["ignore_file"], "scan.ignore_file")
    ignore_file = (root / scan.get("ignore_file", ".roadcredentialsignore")).resolve()
    connector_runtime = _object(
        raw.get("connector_runtime"),
        "connector_runtime",
        allowed={"id", "transport", "dispatch"},
        required={"id", "transport", "dispatch"},
    )
    connector_runtime_id = connector_runtime.get("id")
    connector_runtime_id = _non_empty_string(connector_runtime_id, "connector_runtime.id")
    if connector_runtime.get("transport") != "connector_rpc":
        raise ConfigError("connector_runtime.transport must be connector_rpc")
    connector_dispatch = _command(connector_runtime.get("dispatch"), "connector_runtime.dispatch")

    credential_values = raw.get("credentials")
    if not isinstance(credential_values, list):
        raise ConfigError("credentials must be an array")
    credentials: list[Credential] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(credential_values):
        where = f"credentials[{index}]"
        item = _object(
            item,
            where,
            allowed={"id", "connector", "risk", "provider_id", "auto_heal", "detect", "lifecycle", "consumers"},
            required={"id", "connector", "risk", "provider_id", "auto_heal", "detect", "lifecycle", "consumers"},
        )
        credential_id = _non_empty_string(item.get("id"), f"{where}.id")
        if credential_id in seen_ids:
            raise ConfigError(f"duplicate credential id: {credential_id}")
        seen_ids.add(credential_id)
        connector = _non_empty_string(item.get("connector"), f"{where}.connector")
        risk = _non_empty_string(item.get("risk"), f"{where}.risk")
        provider_id = item.get("provider_id")
        if provider_id is not None:
            provider_id = _non_empty_string(provider_id, f"{where}.provider_id")
        auto_heal = item.get("auto_heal")
        if not isinstance(auto_heal, bool):
            raise ConfigError(f"{where}.auto_heal must be a boolean")
        detect = _object(
            item.get("detect"),
            f"{where}.detect",
            allowed={"kinds", "names", "paths", "fingerprints"},
        )
        lifecycle = _object(
            item.get("lifecycle"),
            f"{where}.lifecycle",
            allowed={
                "authorize_action", "create_action", "validate_action", "activate_action",
                "restore_action", "revoke_old_action", "revoke_new_action",
            },
            required={
                "create_action", "validate_action", "activate_action", "restore_action",
                "revoke_old_action", "revoke_new_action",
            },
        )
        consumer_values = item.get("consumers")
        if not isinstance(consumer_values, list):
            raise ConfigError(f"{where}.consumers must be an array")
        consumers: list[Consumer] = []
        consumer_ids: set[str] = set()
        for c_index, consumer in enumerate(consumer_values):
            c_where = f"{where}.consumers[{c_index}]"
            consumer = _object(
                consumer,
                c_where,
                allowed={"id", "paths", "update_action", "verify_action", "rollback_action"},
                required={"id", "paths", "update_action", "verify_action", "rollback_action"},
            )
            consumer_id = _non_empty_string(consumer.get("id"), f"{c_where}.id")
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
                connector=connector,
                risk=risk,
                provider_id=provider_id,
                kinds=_strings(detect.get("kinds"), f"{where}.detect.kinds"),
                names=_strings(detect.get("names"), f"{where}.detect.names"),
                paths=_strings(detect.get("paths"), f"{where}.detect.paths"),
                fingerprints=_strings(detect.get("fingerprints"), f"{where}.detect.fingerprints"),
                auto_heal=auto_heal,
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
        max_file_bytes=_positive_int(scan.get("max_file_bytes", 2_000_000), "scan.max_file_bytes"),
        history_max_bytes=_positive_int(scan.get("history_max_bytes", 25_000_000), "scan.history_max_bytes"),
        reference_ignore_paths=_strings(scan.get("reference_ignore_paths"), "scan.reference_ignore_paths"),
        connector_runtime_id=connector_runtime_id,
        connector_dispatch=connector_dispatch,
        credentials=tuple(credentials),
    )
