from __future__ import annotations

import unittest

from road_credentials.protocol import ProtocolError, validate_request
from road_credentials.routes import rotation_route


class ProtocolTests(unittest.TestCase):
    def request(self, phase="create_new", consumer_id=None, new_provider_id=None):
        return {
            "schema_version": 2,
            "route": rotation_route(
                runtime_id="runtime", connector_id="github", credential_id="ci",
                rotation_id="rotation-1", consumer_id=consumer_id,
            ),
            "connector_runtime_id": "runtime",
            "connector": "github",
            "credential_id": "ci",
            "rotation_id": "rotation-1",
            "phase": phase,
            "action": "credential.action",
            "risk": "medium",
            "approved_risk": "medium",
            "old_provider_id": "provider-old",
            "new_provider_id": new_provider_id,
            "consumer_id": consumer_id,
        }

    def test_valid_create_request(self):
        request = self.request()
        self.assertEqual(request, validate_request(request, connector_runtime_id="runtime"))

    def test_valid_consumer_request(self):
        request = self.request("update_consumer", "primary", "provider-new")
        self.assertEqual(request, validate_request(request, connector_runtime_id="runtime"))

    def test_unknown_and_missing_fields_are_rejected(self):
        unknown = self.request()
        unknown["credential_value"] = "forbidden"
        with self.assertRaisesRegex(ProtocolError, "unknown fields"):
            validate_request(unknown, connector_runtime_id="runtime")
        missing = self.request()
        del missing["route"]
        with self.assertRaisesRegex(ProtocolError, "missing fields"):
            validate_request(missing, connector_runtime_id="runtime")

    def test_runtime_and_route_must_match(self):
        with self.assertRaisesRegex(ProtocolError, "configured runtime"):
            validate_request(self.request(), connector_runtime_id="different")
        request = self.request()
        request["route"] += "/admin"
        with self.assertRaisesRegex(ProtocolError, "Route does not match"):
            validate_request(request, connector_runtime_id="runtime")

    def test_schema_is_exact_integer_two(self):
        for schema in (1, 3, True, "2"):
            with self.subTest(schema=schema):
                request = self.request()
                request["schema_version"] = schema
                with self.assertRaisesRegex(ProtocolError, "schema_version"):
                    validate_request(request, connector_runtime_id="runtime")

    def test_phase_is_allowlisted(self):
        request = self.request()
        for phase in ("shell_execute", [], None):
            with self.subTest(phase=phase):
                request["phase"] = phase
                with self.assertRaisesRegex(ProtocolError, "phase is not supported"):
                    validate_request(request, connector_runtime_id="runtime")

    def test_action_is_bounded_and_structured(self):
        for action in ("", " action", "a b", "x" * 257):
            with self.subTest(action=action):
                request = self.request()
                request["action"] = action
                with self.assertRaisesRegex(ProtocolError, "action is invalid"):
                    validate_request(request, connector_runtime_id="runtime")

    def test_identifiers_are_trimmed_and_bounded(self):
        for value in ("", " value", "value ", "x" * 1025, 7):
            with self.subTest(value=value):
                request = self.request()
                request["credential_id"] = value
                with self.assertRaisesRegex(ProtocolError, "credential_id"):
                    validate_request(request, connector_runtime_id="runtime")

    def test_consumer_phase_requires_consumer_and_matching_route(self):
        request = self.request("update_consumer", None, "provider-new")
        with self.assertRaisesRegex(ProtocolError, "requires consumer_id"):
            validate_request(request, connector_runtime_id="runtime")
        request = self.request("create_new", "primary", None)
        with self.assertRaisesRegex(ProtocolError, "must not include consumer_id"):
            validate_request(request, connector_runtime_id="runtime")

    def test_new_provider_phase_rules(self):
        with self.assertRaisesRegex(ProtocolError, "requires new_provider_id"):
            validate_request(self.request("validate_new"), connector_runtime_id="runtime")
        with self.assertRaisesRegex(ProtocolError, "must not include new_provider_id"):
            validate_request(self.request("create_new", new_provider_id="provider-new"), connector_runtime_id="runtime")
        with self.assertRaisesRegex(ProtocolError, "must differ"):
            validate_request(self.request("validate_new", new_provider_id="provider-old"), connector_runtime_id="runtime")

    def test_risk_must_be_valid_and_approved(self):
        request = self.request()
        request["risk"] = "critical"
        with self.assertRaisesRegex(ProtocolError, "exceeds"):
            validate_request(request, connector_runtime_id="runtime")
        request["approved_risk"] = "everything"
        with self.assertRaisesRegex(ProtocolError, "risk level is invalid"):
            validate_request(request, connector_runtime_id="runtime")
        request = self.request()
        request["risk"] = []
        with self.assertRaisesRegex(ProtocolError, "risk level is invalid"):
            validate_request(request, connector_runtime_id="runtime")


if __name__ == "__main__":
    unittest.main()
