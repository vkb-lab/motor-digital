from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.operator_approval_console.console import OperatorApprovalConsole
from k_atlas.core.operator_approval_console.policy import validate_approval_request


class OperatorApprovalConsoleSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_approval_console_"))
        self.console = OperatorApprovalConsole(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_execute(self) -> None:
        result = validate_approval_request({"action_type": "mission_install", "title": "x", "auto_execute": True})
        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_create_and_decide(self) -> None:
        item = self.console.create_request({"action_type": "mission_install", "title": "Demo", "auto_execute": False})
        self.assertEqual(item["status"], "waiting_operator_decision")
        decided = self.console.decide(item["approval_request_id"], "approve", notes="ok")
        self.assertEqual(decided["status"], "approved_by_operator")
        summary = self.console.summary()
        self.assertEqual(summary["summary"]["approved_by_operator"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/80_K_Atlas_Operator_Approval_Console.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
