from __future__ import annotations

import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "src"))

from road_network.unifi import (
    UniFiConfig,
    UniFiError,
    choose_site,
    normalize_base_url,
    plan_unifi,
)


class UniFiConfigTests(unittest.TestCase):
    def test_gateway_origin_normalizes_to_integration_api(self) -> None:
        self.assertEqual(
            normalize_base_url("https://10.17.10.1"),
            "https://10.17.10.1/proxy/network/integration",
        )

    def test_explicit_integration_base_is_preserved(self) -> None:
        self.assertEqual(
            normalize_base_url("https://unifi.example/integration/"),
            "https://unifi.example/integration",
        )

    def test_public_config_never_contains_api_key(self) -> None:
        config = UniFiConfig(
            base_url="https://router/proxy/network/integration",
            api_key="super-secret-key",
        )
        public = config.public()
        self.assertNotIn("super-secret-key", repr(public))
        self.assertNotIn("api_key", public)
        self.assertTrue(public["api_key_configured"])

    def test_site_selection_requires_disambiguation(self) -> None:
        with self.assertRaises(UniFiError):
            choose_site(
                [{"id": "one", "name": "A"}, {"id": "two", "name": "B"}],
                site_id=None,
                site_name=None,
            )


class UniFiPlannerTests(unittest.TestCase):
    @staticmethod
    def desired(networks: list[dict]) -> dict:
        return {
            "digest": "sha256:test",
            "artifacts": {"unifi": {"networks": networks}},
        }

    @staticmethod
    def observed(networks: list[dict], zones: list[dict]) -> dict:
        return {
            "site": {"id": "site-1", "name": "Default"},
            "capabilities": {
                "application_version": "10.1.84",
                "network_crud": True,
                "firewall_zone_crud": True,
                "firewall_policy_crud": True,
            },
            "networks": networks,
            "zones": zones,
        }

    def test_matching_network_and_zone_are_idempotent(self) -> None:
        desired = self.desired(
            [
                {
                    "id": "road.management",
                    "vlan": 10,
                    "cidr": "10.17.10.0/24",
                    "gateway": "10.17.10.1",
                }
            ]
        )
        observed = self.observed(
            [
                {
                    "id": "net-10",
                    "name": "road.management",
                    "vlanId": 10,
                    "enabled": True,
                }
            ],
            [
                {
                    "id": "zone-10",
                    "name": "road.management",
                    "networkIds": ["net-10"],
                }
            ],
        )
        plan = plan_unifi(desired, observed)
        self.assertEqual(plan["changes"], 0)
        self.assertEqual(plan["blockers"], [])
        self.assertEqual(plan["destructive_operations"], 0)
        self.assertFalse(plan["provider_write_enabled"])

    def test_missing_network_plans_non_destructive_create(self) -> None:
        desired = self.desired(
            [{"id": "road.compute", "vlan": 30, "cidr": "10.17.30.0/24"}]
        )
        plan = plan_unifi(desired, self.observed([], []))
        self.assertEqual(plan["changes"], 1)
        self.assertEqual(plan["operations"][0]["action"], "create")
        self.assertEqual(plan["operations"][0]["body"]["vlanId"], 30)
        self.assertEqual(plan["destructive_operations"], 0)

    def test_vlan_collision_blocks_instead_of_renaming_by_guess(self) -> None:
        desired = self.desired(
            [{"id": "road.compute", "vlan": 30, "cidr": "10.17.30.0/24"}]
        )
        observed = self.observed(
            [{"id": "existing-30", "name": "SomebodyElse", "vlanId": 30}],
            [],
        )
        plan = plan_unifi(desired, observed)
        self.assertEqual(plan["changes"], 0)
        self.assertEqual(len(plan["blockers"]), 1)
        self.assertEqual(
            plan["blockers"][0]["reason"],
            "vlan-already-owned-by-different-network",
        )

    def test_old_network_version_blocks_write_plan(self) -> None:
        desired = self.desired([{"id": "road.lab", "vlan": 70}])
        observed = self.observed([], [])
        observed["capabilities"]["application_version"] = "9.4.19"
        observed["capabilities"]["network_crud"] = False
        plan = plan_unifi(desired, observed)
        self.assertTrue(plan["blockers"])
        self.assertEqual(
            plan["blockers"][0]["reason"],
            "unifi-network-version-too-old",
        )


if __name__ == "__main__":
    unittest.main()
