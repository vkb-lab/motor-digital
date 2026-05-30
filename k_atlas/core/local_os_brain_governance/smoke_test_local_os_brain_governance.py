from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_os_brain_governance.brain import LocalOSBrainGovernance
from k_atlas.core.local_os_brain_governance.policy import validate_brain_request


class LocalOSBrainGovernanceSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_brain_governance_"))
        self.brain = LocalOSBrainGovernance(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_safe_action(self) -> None:
        result = validate_brain_request({
            "agent": "mission_generator",
            "action": "create_local_mission",
            "auto_execute": False,
            "real_execution_enabled": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "approved_safe")
        self.assertFalse(result["automatic_execution_allowed"])

    def test_sensitive_action_requires_human(self) -> None:
        decision = self.brain.decide({
            "agent": "execution_agent",
            "action": "apply_local_change",
            "auto_execute": False,
            "real_execution_enabled": False,
        })

        self.assertTrue(decision["ok"])
        self.assertEqual(decision["status"], "requires_human_approval")
        self.assertTrue(decision["human_approval_required"])

    def test_blocked_action(self) -> None:
        decision = self.brain.decide({
            "agent": "remote_assist_agent",
            "action": "control_mouse",
        })

        self.assertFalse(decision["ok"])
        self.assertEqual(decision["status"], "blocked")

    def test_feedback_and_report(self) -> None:
        decision = self.brain.decide({
            "agent": "mission_generator",
            "action": "create_local_mission",
        })
        feedback = self.brain.route_feedback(decision)
        report = self.brain.build_report()

        self.assertTrue(feedback["ok"])
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "133")
        self.assertTrue((self.tmp / "live" / "local_os_brain_governance" / "brain_decision_queue.json").exists())
        self.assertTrue((self.tmp / "reports" / "local_os_brain_governance" / "latest_local_os_brain_governance.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/133_K_Atlas_Local_OS_Brain_Governance.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
