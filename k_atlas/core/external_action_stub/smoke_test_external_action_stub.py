from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.external_action_stub.policy import validate_external_action_execution_payload
from k_atlas.core.external_action_stub.stub import ExternalActionExecutionStub
from k_atlas.core.publish_approval_gate.gate import SecurePublishApprovalGate


class ExternalActionStubSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_external_action_stub_"))
        self.gate = SecurePublishApprovalGate(
            reports_dir=self.tmp / "gate_reports",
            memory_dir=self.tmp / "gate_memory",
        )
        self.stub = ExternalActionExecutionStub(
            reports_dir=self.tmp / "stub_reports",
            memory_dir=self.tmp / "stub_memory",
            approval_gate=self.gate,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_real_execute(self) -> None:
        result = validate_external_action_execution_payload({
            "request_id": "abc",
            "action_type": "instagram_publish",
            "real_execute": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("real_execute_blocked", result["reasons"])

    def test_execute_approved_stub(self) -> None:
        request = self.gate.create_request()
        self.gate.decide(request["request_id"], "approved", "tester", "stub ok")

        result = self.stub.execute_approved_stubs()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "55")
        self.assertEqual(result["executed_stubs"], 1)
        self.assertFalse(result["real_execution_enabled"])
        self.assertTrue((self.tmp / "stub_reports" / "latest_external_action_stub.json").exists())

        loaded = json.loads((self.tmp / "stub_reports" / "latest_external_action_stub.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "55")

    def test_does_not_execute_pending(self) -> None:
        self.gate.create_request()
        result = self.stub.execute_approved_stubs()
        self.assertTrue(result["ok"])
        self.assertEqual(result["executed_stubs"], 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/36_K_Atlas_External_Action_Stub.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
