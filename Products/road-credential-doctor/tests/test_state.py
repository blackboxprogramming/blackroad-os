from __future__ import annotations

import json
import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

from road_credentials.state import MAX_STATE_BYTES, atomic_write_json, empty_state, load_state, validate_state


def operation() -> dict:
    return {
        "credential_id": "github-ci",
        "connector": "github",
        "rotation_id": "rotation-1",
        "stage": "created",
        "old_provider_id": "provider-old",
        "new_provider_id": "provider-new",
        "updated_consumers": [],
        "fingerprints": ["sha256:abc"],
        "created_at": "2026-09-14T00:00:00Z",
        "updated_at": "2026-09-14T00:00:01Z",
    }


def revocation() -> dict:
    return {
        "credential_id": "github-ci",
        "rotation_id": "rotation-2",
        "provider_id": "provider-old",
        "fingerprints": ["sha256:abc"],
        "created_at": "2026-09-14T00:00:02Z",
    }


class StateTests(unittest.TestCase):
    def test_execution_binding_accepts_digest_in_both_queues(self) -> None:
        state = empty_state()
        state["pending_operations"] = [dict(operation(), execution_config_hash="a" * 64)]
        state["pending_revocations"] = [dict(revocation(), execution_config_hash="b" * 64)]
        self.assertIs(state, validate_state(state))

    def test_execution_binding_rejects_malformed_digest_in_both_queues(self) -> None:
        for queue, factory in (("pending_operations", operation), ("pending_revocations", revocation)):
            for value in (None, True, 123, [], {}, "", "a" * 63, "A" * 64, "g" * 64, "a" * 64 + "\n"):
                with self.subTest(queue=queue, value=value):
                    state = empty_state()
                    state[queue] = [dict(factory(), execution_config_hash=value)]
                    with self.assertRaisesRegex(ValueError, "execution_config_hash"):
                        validate_state(state)

    def test_old_state_gets_additive_operation_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text('{"schema_version": 1}', encoding="utf-8")
            state = load_state(path)
        self.assertEqual([], state["pending_operations"])
        self.assertEqual([], state["pending_revocations"])

    def test_valid_operation_and_revocation_are_accepted(self) -> None:
        state = empty_state()
        state["pending_operations"] = [operation()]
        state["pending_revocations"] = [revocation()]
        self.assertIs(state, validate_state(state))

    def test_state_rejects_unknown_root_field(self) -> None:
        state = empty_state()
        state["credential_value"] = "must-not-be-stored"
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            validate_state(state)

    def test_state_rejects_unknown_operation_field(self) -> None:
        state = empty_state()
        item = operation()
        item["token"] = "must-not-be-stored"
        state["pending_operations"] = [item]
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            validate_state(state)

    def test_state_rejects_invalid_operation_shapes(self) -> None:
        mutations = {
            "not_object": lambda item: "bad",
            "bad_stage": lambda item: {**item, "stage": "unknown"},
            "blank_rotation": lambda item: {**item, "rotation_id": " "},
            "non_string_fingerprint": lambda item: {**item, "fingerprints": [7]},
            "non_string_consumer": lambda item: {**item, "updated_consumers": [None]},
            "same_provider": lambda item: {**item, "new_provider_id": item["old_provider_id"]},
            "created_without_provider": lambda item: {**item, "new_provider_id": None},
            "unproven_with_provider": lambda item: {**item, "stage": "create_pending"},
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                state = empty_state()
                state["pending_operations"] = [mutation(operation())]
                with self.assertRaises(ValueError):
                    validate_state(state)

    def test_create_pending_requires_null_replacement(self) -> None:
        state = empty_state()
        item = operation()
        item.update(stage="create_pending", new_provider_id=None)
        state["pending_operations"] = [item]
        self.assertIs(state, validate_state(state))

    def test_duplicate_operation_ids_are_rejected(self) -> None:
        state = empty_state()
        state["pending_operations"] = [operation(), deepcopy(operation())]
        with self.assertRaisesRegex(ValueError, "duplicate pending operation"):
            validate_state(state)

    def test_duplicate_revocation_ids_are_rejected(self) -> None:
        state = empty_state()
        state["pending_revocations"] = [revocation(), deepcopy(revocation())]
        with self.assertRaisesRegex(ValueError, "duplicate pending revocation"):
            validate_state(state)

    def test_same_rotation_cannot_exist_in_both_queues(self) -> None:
        state = empty_state()
        pending = revocation()
        pending["rotation_id"] = operation()["rotation_id"]
        state["pending_operations"] = [operation()]
        state["pending_revocations"] = [pending]
        with self.assertRaisesRegex(ValueError, "operation-pending and revocation-pending"):
            validate_state(state)

    def test_rotation_id_cannot_escape_receipt_directory(self) -> None:
        state = empty_state()
        item = operation()
        item["rotation_id"] = "../../outside"
        state["pending_operations"] = [item]
        with self.assertRaisesRegex(ValueError, "unsafe characters"):
            validate_state(state)

    def test_duplicate_json_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
                load_state(path)

    def test_oversized_state_is_rejected_before_json_parse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            with path.open("wb") as handle:
                handle.truncate(MAX_STATE_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "state exceeds"):
                load_state(path)

    def test_excessive_state_nesting_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("[" * 2000 + "]" * 2000, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_state(path)

    def test_atomic_write_replaces_complete_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            atomic_write_json(path, {"generation": 1})
            atomic_write_json(path, {"generation": 2})
            self.assertEqual({"generation": 2}, json.loads(path.read_text(encoding="utf-8")))
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual([], list(path.parent.glob(f".{path.name}.*")))

    def test_atomic_write_fsyncs_file_and_directory(self) -> None:
        calls: list[int] = []
        real_fsync = os.fsync

        def recording_fsync(descriptor: int) -> None:
            calls.append(descriptor)
            real_fsync(descriptor)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            with mock.patch("road_credentials.state.os.fsync", side_effect=recording_fsync):
                atomic_write_json(path, {"generation": 1})
        self.assertEqual(2, len(calls))


if __name__ == "__main__":
    unittest.main()
