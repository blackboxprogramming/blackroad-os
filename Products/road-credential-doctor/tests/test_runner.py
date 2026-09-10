import json
import sys
import tempfile
import unittest
from pathlib import Path

from road_credentials.models import CommandSpec
from road_credentials.runner import dispatch_connector


class RunnerTests(unittest.TestCase):
    def invoke(self, program, timeout=2):
        with tempfile.TemporaryDirectory() as directory:
            return dispatch_connector(
                CommandSpec((sys.executable, "-c", program), timeout_seconds=timeout),
                cwd=Path(directory), connector_runtime_id="test-host", request={"action": "probe"},
            )

    def response(self, **changes):
        response = dict(ok=True, execution_id="execution-1", authority="connector", secret_material=False)
        response.update(changes)
        return response

    def test_valid_response(self):
        result = self.invoke("print(" + repr(json.dumps(self.response())) + ")")
        self.assertTrue(result.ok)

    def test_overflow_is_rejected_before_waiting_for_exit(self):
        result = self.invoke("import os,time; os.write(1,b'x'*65537); time.sleep(10)", timeout=0.5)
        self.assertFalse(result.ok)
        self.assertEqual(65, result.returncode)

    def test_stalled_process_times_out(self):
        result = self.invoke("import time; time.sleep(10)", timeout=0.1)
        self.assertFalse(result.ok)
        self.assertEqual(124, result.returncode)

    def test_duplicate_json_fields_are_rejected(self):
        payload = json.dumps(self.response())[:-1] + ',"ok":false,"ok":true}'
        self.assertFalse(self.invoke("print(" + repr(payload) + ")").ok)

    def test_whitespace_execution_id_is_rejected(self):
        self.assertFalse(self.invoke("print(" + repr(json.dumps(self.response(execution_id="  "))) + ")").ok)

    def test_deep_json_is_rejected_without_crashing(self):
        result = self.invoke("print('['*1500 + '0' + ']'*1500)")
        self.assertFalse(result.ok)

    def test_malformed_and_secret_responses(self):
        for payload in ["not-json", "[]", json.dumps(self.response(secret="do-not-return")), json.dumps(self.response(ok=1))]:
            with self.subTest(payload=payload):
                self.assertFalse(self.invoke("print(" + repr(payload) + ")").ok)

    def test_nonzero_exit_cannot_claim_success(self):
        payload = json.dumps(self.response())
        self.assertFalse(self.invoke("print(" + repr(payload) + "); raise SystemExit(9)").ok)

    def test_exact_limit_valid_response_is_accepted(self):
        payload = json.dumps(self.response())
        program = "import sys; sys.stdout.write(" + repr(payload) + "+' '*(65536-" + str(len(payload)) + "))"
        self.assertTrue(self.invoke(program).ok)

    def test_one_byte_over_limit_is_rejected(self):
        payload = json.dumps(self.response())
        program = "import sys; sys.stdout.write(" + repr(payload) + "+' '*(65537-" + str(len(payload)) + "))"
        self.assertEqual(65, self.invoke(program).returncode)

    def test_inherited_stdout_cannot_hold_parent_forever(self):
        program = "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)'])"
        self.assertEqual(124, self.invoke(program, timeout=0.2).returncode)

    def test_invalid_utf8_is_rejected(self):
        self.assertEqual(65, self.invoke("import os; os.write(1,b'\\xff')").returncode)

    def test_large_input_does_not_deadlock_early_response(self):
        payload = json.dumps(self.response())
        with tempfile.TemporaryDirectory() as directory:
            result = dispatch_connector(
                CommandSpec((sys.executable, "-c", "print(" + repr(payload) + ")"), timeout_seconds=2),
                cwd=Path(directory), connector_runtime_id="test-host", request={"action": "x" * 100000},
            )
        self.assertTrue(result.ok)
