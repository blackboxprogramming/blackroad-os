from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from road_credentials.config import MAX_CONFIG_BYTES, ConfigError, load_config


def valid_config() -> dict:
    return {
        "schema_version": 3,
        "root": ".",
        "connector_runtime": {
            "id": "road-connectors",
            "transport": "connector_rpc",
            "dispatch": ["/bin/true"],
        },
        "runtime": {"state_file": "state.json", "receipt_dir": "receipts"},
        "scan": {
            "ignore_file": ".roadcredentialsignore",
            "max_file_bytes": 1024,
            "history_max_bytes": 2048,
            "reference_ignore_paths": [],
        },
        "credentials": [
            {
                "id": "github-ci",
                "connector": "github",
                "risk": "medium",
                "provider_id": "provider-old",
                "auto_heal": True,
                "detect": {"kinds": ["github_token"], "names": ["GITHUB_TOKEN"], "paths": ["*"]},
                "lifecycle": {
                    "create_action": "credential.create",
                    "validate_action": "credential.validate",
                    "activate_action": "credential.activate",
                    "restore_action": "credential.restore",
                    "revoke_old_action": "credential.revoke-old",
                    "revoke_new_action": "credential.revoke-new",
                },
                "consumers": [
                    {
                        "id": "primary",
                        "paths": [".env"],
                        "update_action": "consumer.update",
                        "verify_action": "consumer.verify",
                        "rollback_action": "consumer.rollback",
                    }
                ],
            }
        ],
    }


class ConfigTests(unittest.TestCase):
    def _load(self, payload) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credentials.json"
            if isinstance(payload, bytes):
                path.write_bytes(payload)
            elif isinstance(payload, str):
                path.write_text(payload, encoding="utf-8")
            else:
                path.write_text(json.dumps(payload), encoding="utf-8")
            load_config(path)

    def test_valid_strict_config_loads(self) -> None:
        self._load(valid_config())

    def test_duplicate_json_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigError, "duplicate JSON field"):
            self._load('{"schema_version":3,"schema_version":3,"connector_runtime":{},"credentials":[]}')

    def test_non_object_root_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigError, "configuration must be an object"):
            self._load([])

    def test_unknown_fields_fail_closed_at_every_level(self) -> None:
        mutations = {
            "root": lambda cfg: cfg.update(token="forbidden"),
            "runtime": lambda cfg: cfg["runtime"].update(token="forbidden"),
            "scan": lambda cfg: cfg["scan"].update(token="forbidden"),
            "connector_runtime": lambda cfg: cfg["connector_runtime"].update(token="forbidden"),
            "credential": lambda cfg: cfg["credentials"][0].update(token="forbidden"),
            "detect": lambda cfg: cfg["credentials"][0]["detect"].update(token="forbidden"),
            "lifecycle": lambda cfg: cfg["credentials"][0]["lifecycle"].update(token="forbidden"),
            "consumer": lambda cfg: cfg["credentials"][0]["consumers"][0].update(token="forbidden"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                config = deepcopy(valid_config())
                mutate(config)
                with self.assertRaisesRegex(ConfigError, "unknown fields"):
                    self._load(config)

    def test_string_false_is_not_accepted_as_auto_heal(self) -> None:
        config = valid_config()
        config["credentials"][0]["auto_heal"] = "false"
        with self.assertRaisesRegex(ConfigError, "auto_heal must be a boolean"):
            self._load(config)

    def test_scan_limits_require_positive_integers(self) -> None:
        for value in (True, 0, -1, "1024", 1.5):
            with self.subTest(value=value):
                config = valid_config()
                config["scan"]["max_file_bytes"] = value
                with self.assertRaisesRegex(ConfigError, "positive integer"):
                    self._load(config)

    def test_credentials_must_be_an_array(self) -> None:
        config = valid_config()
        config["credentials"] = {}
        with self.assertRaisesRegex(ConfigError, "credentials must be an array"):
            self._load(config)

    def test_whitespace_identifiers_are_rejected(self) -> None:
        for target in ("runtime", "credential", "consumer"):
            with self.subTest(target=target):
                config = valid_config()
                if target == "runtime":
                    config["connector_runtime"]["id"] = " "
                elif target == "credential":
                    config["credentials"][0]["id"] = " "
                else:
                    config["credentials"][0]["consumers"][0]["id"] = " "
                with self.assertRaisesRegex(ConfigError, "non-empty"):
                    self._load(config)

    def test_invalid_utf8_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigError, "valid UTF-8"):
            self._load(b"\xff\xfe")

    def test_oversized_configuration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credentials.json"
            with path.open("wb") as handle:
                handle.truncate(MAX_CONFIG_BYTES + 1)
            with self.assertRaisesRegex(ConfigError, "configuration exceeds"):
                load_config(path)

    def test_excessive_json_nesting_is_rejected(self) -> None:
        nested = "[" * 2000 + "]" * 2000
        with self.assertRaises(ConfigError):
            self._load(nested)


if __name__ == "__main__":
    unittest.main()
