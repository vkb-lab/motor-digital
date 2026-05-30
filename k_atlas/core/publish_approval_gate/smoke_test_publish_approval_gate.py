from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.publish_approval_gate.gate import SecurePublishApprovalGate
from k_atlas.core.publish_approval_gate.policy import validate_publish_approval_payload


class PublishApprovalGateSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_publish_gate_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_publish(self) -> None:
        result = validate_publish_approval_payload({
            "title": "Teste",
            "objective": "validar",
            "action_type": "instagram_publish",
            "channel": "instagram",
            "auto_publish": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("auto_publish_blocked", result["reasons"])

    def test_policy_blocks_live_without_approval(self) -> None:
        result = validate_publish_approval_payload({
            "title": "Teste",
            "objective": "validar",
            "action_type": "external_api_call",
            "channel": "openai",
            "live_call": True,
            "human_approved": False,
        })

        self.assertFalse(result["ok"])
        self.assertIn("live_call_requires_human_approval", result["reasons"])

    def test_create_and_decide(self) -> None:
        gate = SecurePublishApprovalGate(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        request = gate.create_request()
        self.assertTrue(request["ok"])
        self.assertEqual(request["checkpoint"], "54")
        self.assertFalse(request["execution_allowed"])

        decision = gate.decide(request["request_id"], "approved", "tester", "ok")
        self.assertTrue(decision["ok"])
        self.assertEqual(decision["status"], "approved_waiting_execution_gate")
        self.assertFalse(decision["decision"]["execution_allowed"])

        report = gate.save_report()
        self.assertTrue(report["ok"])
        self.assertFalse(report["execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_publish_approval_gate.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_publish_approval_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "54")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/35_K_Atlas_Secure_Publish_Approval_Gate.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
