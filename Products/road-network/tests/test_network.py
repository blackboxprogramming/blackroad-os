from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PACKAGE_ROOT / "src"))

from road_network.compiler import apply_local, compile_state, load_canon, load_current_state, plan_changes, validate_canon
from road_network.yamlmini import parse_simple_yaml


class MiniYAMLTests(unittest.TestCase):
    def test_nested_maps_lists_and_inline_values(self) -> None:
        document = parse_simple_yaml(
            """
schema: test.v1
defaults:
  deny: true
zones:
  road.lab:
    routes: [dns, ntp]
items:
  - { id: one, vlan: 10 }
  - id: two
    vlan: 20
"""
        )
        self.assertEqual(document["defaults"]["deny"], True)
        self.assertEqual(document["zones"]["road.lab"]["routes"], ["dns", "ntp"])
        self.assertEqual(document["items"][1]["vlan"], 20)


class CanonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.canon = load_canon(REPO_ROOT)

    def test_checked_in_canon_is_valid(self) -> None:
        report = validate_canon(self.canon)
        self.assertEqual(report["errors"], [])

    def test_compiler_keeps_1729_control_plane(self) -> None:
        state = compile_state(self.canon)
        control = state["resources"]["network:road.control"]
        self.assertEqual(control["vlan"], 1729)
        self.assertEqual(control["cidr"], "10.17.29.0/24")
        self.assertTrue(state["digest"].startswith("sha256:"))

    def test_local_apply_is_idempotent(self) -> None:
        desired = compile_state(self.canon)
        first = plan_changes(desired, {"resources": {}})
        self.assertGreater(first["changes"], 0)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            receipt = apply_local(desired, output)
            self.assertFalse(receipt["provider_mutated"])
            current = load_current_state(output / "state.json")
            second = plan_changes(desired, current)
            self.assertEqual(second["changes"], 0)
            self.assertTrue((output / "unifi.json").is_file())
            self.assertTrue((output / "dns.json").is_file())
            self.assertTrue((output / "fleet.json").is_file())

    def test_no_credential_fields_in_compiled_dns(self) -> None:
        desired = compile_state(self.canon)
        sensitive_keys = {
            "password",
            "token",
            "api_key",
            "private_key",
            "credential",
            "secret_value",
        }

        def walk(value: object) -> None:
            if isinstance(value, dict):
                self.assertTrue(sensitive_keys.isdisjoint(value.keys()))
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)

        walk(desired["artifacts"]["dns"])


if __name__ == "__main__":
    unittest.main()
