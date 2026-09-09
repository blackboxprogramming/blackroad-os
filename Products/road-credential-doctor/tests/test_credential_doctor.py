from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from road_credentials.catalog import connector_catalog
from road_credentials.cli import EXIT_BLOCKED, EXIT_FINDINGS, EXIT_OK, _mapping, main
from road_credentials.config import ConfigError, load_config
from road_credentials.doctor import run_doctor
from road_credentials.inventory import coverage_report
from road_credentials.rotation import rotate
from road_credentials.rotation import reconcile_pending
from road_credentials.scanner import scan
from road_credentials.scanner import ScanIncomplete
from road_credentials.state import load_state


LEAKED = "ghp_" + "A1b2C3d4" * 5
HOOK = Path(__file__).with_name("fixture_hook.py").resolve()


class CredentialDoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.runtime = self.base / "runtime"
        self.runtime.mkdir()
        self.runtime.chmod(0o700)
        (self.runtime / "consumer-primary").write_text("provider-old", encoding="utf-8")
        (self.repo / ".env").write_text(f"GITHUB_TOKEN={LEAKED}\n", encoding="utf-8")
        self.config_path = self.base / "credentials.json"
        self.config_path.write_text(json.dumps(self._config()), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _command(self) -> list[str]:
        return [sys.executable, str(HOOK), str(self.runtime)]

    def _config(self) -> dict:
        return {
            "schema_version": 3,
            "root": "repo",
            "connector_runtime": {
                "id": "blackroad-connectors-test",
                "transport": "connector_rpc",
                "dispatch": self._command(),
            },
            "runtime": {
                "state_file": "runtime/state.json",
                "receipt_dir": "runtime/receipts",
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

    def _rotate(self):
        settings = load_config(self.config_path)
        findings = scan(settings)
        return settings, findings, rotate(settings, settings.credentials[0], findings, approved_risk="medium")

    def _events(self) -> list[str]:
        return (self.runtime / "events.log").read_text(encoding="utf-8").splitlines()

    def test_scanner_redacts_secret_values(self) -> None:
        settings = load_config(self.config_path)
        findings = scan(settings)
        self.assertEqual(1, len(findings))
        public = json.dumps([item.public() for item in findings])
        self.assertNotIn(LEAKED, public)
        self.assertIn("sha256:", public)

    def test_manual_rotation_without_consumers_is_blocked(self) -> None:
        config = self._config()
        config["credentials"][0]["consumers"] = []
        config["credentials"][0]["auto_heal"] = False
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "consumer"):
            self._rotate()
        self.assertFalse((self.runtime / "events.log").exists())

    def test_rotation_without_provider_id_is_blocked_in_engine(self) -> None:
        config = self._config()
        config["credentials"][0]["provider_id"] = ""
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "provider id"):
            self._rotate()
        self.assertFalse((self.runtime / "events.log").exists())

    def test_pending_revocation_blocks_another_rotation(self) -> None:
        (self.runtime / "fail_phase").write_text("revoke_old", encoding="utf-8")
        settings, findings, outcome = self._rotate()
        self.assertEqual("pending_revocation", outcome.status)
        events_before = self._events()
        with self.assertRaisesRegex(ValueError, "pending revocation"):
            rotate(settings, settings.credentials[0], findings, approved_risk="medium")
        self.assertEqual(events_before, self._events())

    def test_reference_inventory_is_covered_by_declared_consumer(self) -> None:
        report = coverage_report(load_config(self.config_path))
        self.assertEqual(1, report["references"])
        self.assertEqual([], report["uncovered"])
        self.assertEqual([], report["unregistered"])
        self.assertEqual("primary", report["covered"][0]["consumers"][0])

    def test_reference_inventory_fails_closed_for_unknown_secret_name(self) -> None:
        (self.repo / "worker.py").write_text('value = os.getenv("CLOUDFLARE_API_TOKEN")\n', encoding="utf-8")
        report = coverage_report(load_config(self.config_path))
        self.assertEqual("CLOUDFLARE_API_TOKEN", report["unregistered"][0]["name"])

    def test_connector_catalog_has_unique_complete_policy_entries(self) -> None:
        catalog = connector_catalog()
        self.assertEqual(69, catalog["counts"]["managed"])
        self.assertEqual(37, catalog["counts"]["user_managed"])
        entries = catalog["managed_connectors"] + catalog["user_managed_connectors"]
        identifiers = [entry["id"] for entry in entries]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for entry in entries:
            self.assertIn(entry["strategy"], catalog["strategies"])
        self.assertTrue(all(entry["local_rotation"] == "prohibited" for entry in entries))
        self.assertTrue(all(entry["execution_plane"].startswith("connector") for entry in entries))

    def test_v2_registry_is_refused_instead_of_unsafely_inferred(self) -> None:
        config = self._config()
        config["schema_version"] = 2
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "schema_version must be 3"):
            load_config(self.config_path)

    def test_unknown_connector_blocks_doctor_and_reconcile(self) -> None:
        config = self._config()
        config["credentials"][0]["connector"] = "not-a-real-connector"
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        checks = run_doctor(load_config(self.config_path))
        self.assertIn("UNKNOWN_CONNECTOR", {check.code for check in checks})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(
                [
                    "--config",
                    str(self.config_path),
                    "--json",
                    "reconcile",
                    "--execute",
                    "--ack-keep-access",
                ]
            )
        self.assertEqual(EXIT_BLOCKED, code)
        self.assertIn("UNKNOWN_CONNECTOR", output.getvalue())
        self.assertFalse((self.runtime / "events.log").exists())

    def test_success_verifies_before_revoking_old(self) -> None:
        settings, findings, outcome = self._rotate()
        self.assertEqual("rotated", outcome.status)
        self.assertTrue(outcome.access_retained)
        self.assertTrue(outcome.old_revoked)
        events = self._events()
        self.assertLess(events.index("baseline_consumer:primary"), events.index("create_new:"))
        self.assertLess(events.index("verify_consumer:primary"), events.index("revoke_old:"))
        self.assertLess(events.index("activate_connector_version:"), events.index("revoke_old:"))
        self.assertEqual("provider-new", (self.runtime / "consumer-primary").read_text(encoding="utf-8"))
        self.assertEqual("provider-new", (self.runtime / "active_provider").read_text(encoding="utf-8"))
        state = load_state(settings.state_file)
        self.assertIn(findings[0].fingerprint, state["retired_fingerprints"])

    def test_consumers_are_canaried_update_then_verify(self) -> None:
        config = self._config()
        config["credentials"][0]["consumers"].append(
            {
                "id": "secondary",
                "paths": ["services/**"],
                "update_action": "consumer.update",
                "verify_action": "consumer.verify",
                "rollback_action": "consumer.rollback",
            }
        )
        (self.runtime / "consumer-secondary").write_text("provider-old", encoding="utf-8")
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("rotated", outcome.status)
        events = self._events()
        self.assertLess(events.index("verify_consumer:primary"), events.index("update_consumer:secondary"))

    def test_verify_failure_rolls_back_and_never_revokes_old(self) -> None:
        (self.runtime / "fail_phase").write_text("verify_consumer", encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("failed_rolled_back", outcome.status)
        self.assertTrue(outcome.access_retained)
        self.assertFalse((self.runtime / "old_revoked").exists())
        self.assertEqual("provider-old", (self.runtime / "consumer-primary").read_text(encoding="utf-8"))
        self.assertIn("rollback_consumer:primary", self._events())

    def test_unhealthy_baseline_stops_before_creating_a_replacement(self) -> None:
        (self.runtime / "fail_phase").write_text("baseline_consumer", encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("failed_rolled_back", outcome.status)
        self.assertNotIn("create_new:", self._events())
        self.assertFalse((self.runtime / "old_revoked").exists())

    def test_connector_activation_failure_rolls_back_and_never_revokes_old(self) -> None:
        (self.runtime / "fail_phase").write_text("activate_connector_version", encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("failed_rolled_back", outcome.status)
        self.assertFalse((self.runtime / "old_revoked").exists())
        self.assertEqual("provider-old", (self.runtime / "consumer-primary").read_text(encoding="utf-8"))

    def test_revoke_failure_is_durable_and_pending(self) -> None:
        (self.runtime / "fail_phase").write_text("revoke_old", encoding="utf-8")
        settings, findings, outcome = self._rotate()
        self.assertEqual("pending_revocation", outcome.status)
        self.assertTrue(outcome.access_retained)
        self.assertEqual("provider-new", (self.runtime / "consumer-primary").read_text(encoding="utf-8"))
        state = load_state(settings.state_file)
        self.assertEqual(1, len(state["pending_revocations"]))
        self.assertNotIn(findings[0].fingerprint, state["retired_fingerprints"])

    def test_pending_revocation_can_be_reconciled_by_provider_id(self) -> None:
        (self.runtime / "fail_phase").write_text("revoke_old", encoding="utf-8")
        settings, findings, outcome = self._rotate()
        self.assertEqual("pending_revocation", outcome.status)
        (self.runtime / "fail_phase").unlink()
        outcomes = reconcile_pending(settings, settings.credentials[0], approved_risk="medium")
        self.assertEqual("revocation_reconciled", outcomes[0].status)
        state = load_state(settings.state_file)
        self.assertEqual([], state["pending_revocations"])
        self.assertIn(findings[0].fingerprint, state["retired_fingerprints"])

    def test_failed_rollback_does_not_claim_access_is_retained(self) -> None:
        (self.runtime / "fail_phase").write_text("verify_consumer rollback_consumer", encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("failed_access_retained", outcome.status)
        self.assertFalse(outcome.access_retained)
        self.assertFalse((self.runtime / "old_revoked").exists())

    def test_receipt_never_contains_secret_values(self) -> None:
        _settings, _findings, outcome = self._rotate()
        receipt = Path(outcome.receipt_path).read_text(encoding="utf-8")
        self.assertNotIn(LEAKED, receipt)
        self.assertIn("receipt_hash", receipt)
        self.assertIn("connector_execution_id", receipt)

    def test_doctor_detects_receipt_tampering(self) -> None:
        settings, _findings, outcome = self._rotate()
        receipt_path = Path(outcome.receipt_path)
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload["status"] = "forged"
        receipt_path.write_text(json.dumps(payload), encoding="utf-8")
        checks = run_doctor(settings)
        self.assertIn("RECEIPT_TAMPERED", {check.code for check in checks})

    def test_doctor_detects_secret_in_command_argument(self) -> None:
        config = self._config()
        config["connector_runtime"]["dispatch"].append(LEAKED)
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        checks = run_doctor(load_config(self.config_path))
        self.assertIn("SECRET_IN_COMMAND", {check.code for check in checks})

    def test_heal_is_dry_run_by_default(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--config", str(self.config_path), "--json", "heal", "--all"])
        self.assertEqual(EXIT_FINDINGS, code)
        self.assertFalse((self.runtime / "events.log").exists())
        self.assertNotIn(LEAKED, output.getvalue())

    def test_critical_rotation_requires_explicit_risk_approval(self) -> None:
        config = self._config()
        config["credentials"][0]["risk"] = "critical"
        config["credentials"][0]["auto_heal"] = False
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(
                [
                    "--config",
                    str(self.config_path),
                    "--json",
                    "heal",
                    "--all",
                    "--execute",
                    "--ack-keep-access",
                ]
            )
        self.assertEqual(EXIT_BLOCKED, code)
        self.assertFalse((self.runtime / "events.log").exists())
        self.assertIn("risk_approval_blockers", output.getvalue())

    def test_rotation_engine_itself_enforces_risk_approval(self) -> None:
        config = self._config()
        config["credentials"][0]["risk"] = "critical"
        config["credentials"][0]["auto_heal"] = False
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        settings = load_config(self.config_path)
        with self.assertRaises(ValueError):
            rotate(settings, settings.credentials[0], scan(settings), approved_risk="medium")
        self.assertFalse((self.runtime / "events.log").exists())

    def test_high_risk_requires_authorization_adapter_even_with_flag(self) -> None:
        config = self._config()
        config["credentials"][0]["risk"] = "critical"
        config["credentials"][0]["auto_heal"] = False
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        settings = load_config(self.config_path)
        with self.assertRaises(ValueError):
            rotate(settings, settings.credentials[0], scan(settings), approved_risk="critical")

    def test_high_risk_authorization_adapter_gates_rotation(self) -> None:
        config = self._config()
        config["credentials"][0]["risk"] = "critical"
        config["credentials"][0]["auto_heal"] = False
        config["credentials"][0]["lifecycle"]["authorize_action"] = "carkeys.authorize"
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            code = main(
                [
                    "--config",
                    str(self.config_path),
                    "--json",
                    "heal",
                    "--all",
                    "--execute",
                    "--ack-keep-access",
                    "--approve-risk",
                    "critical",
                ]
            )
        self.assertEqual(EXIT_OK, code)
        self.assertLess(self._events().index("authorize_rotation:"), self._events().index("create_new:"))

    def test_adapter_does_not_inherit_unrelated_ambient_secret(self) -> None:
        with mock.patch.dict(os.environ, {"UNRELATED_SECRET_TOKEN": "must-not-cross-boundary"}):
            _settings, _findings, outcome = self._rotate()
        self.assertEqual("rotated", outcome.status)

    def test_connector_requests_never_contain_credential_values(self) -> None:
        self._rotate()
        requests = (self.runtime / "requests.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(LEAKED, requests)
        self.assertNotIn("secret", requests.lower())
        for line in requests.splitlines():
            payload = json.loads(line)
            self.assertEqual("blackroad-connectors-test", payload["connector_runtime_id"])

    def test_connector_response_with_secret_field_is_rejected(self) -> None:
        (self.runtime / "malicious_response").write_text("1", encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("failed_rolled_back", outcome.status)
        self.assertFalse((self.runtime / "old_revoked").exists())

    def test_connector_cannot_relabel_the_old_provider_id_as_new(self) -> None:
        (self.runtime / "same_provider_id").write_text("1", encoding="utf-8")
        _settings, _findings, outcome = self._rotate()
        self.assertEqual("failed_rolled_back", outcome.status)
        self.assertFalse((self.runtime / "old_revoked").exists())
        self.assertIn("revoke_unused_replacement:", self._events())

    def test_git_history_scan_finds_deleted_secret(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "doctor@example.invalid"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Credential Doctor Test"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", ".env"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "add fixture"], cwd=self.repo, check=True)
        (self.repo / ".env").unlink()
        subprocess.run(["git", "add", "-u"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "remove fixture"], cwd=self.repo, check=True)
        findings = scan(load_config(self.config_path), include_history=True)
        self.assertTrue(any(item.source == "git_history" and item.fingerprint for item in findings))
        history_only = [item for item in findings if item.source == "git_history"]
        grouped, blocked = _mapping(load_config(self.config_path), history_only)
        self.assertIn("github-ci", grouped)
        self.assertEqual([], blocked)

    def test_truncated_history_scan_is_blocking_not_false_clean(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "doctor@example.invalid"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Credential Doctor Test"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", ".env"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "add fixture"], cwd=self.repo, check=True)
        config = self._config()
        config["scan"] = {"history_max_bytes": 32}
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(ScanIncomplete):
            scan(load_config(self.config_path), include_history=True)


if __name__ == "__main__":
    unittest.main()
