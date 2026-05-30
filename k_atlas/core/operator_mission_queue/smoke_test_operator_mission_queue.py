from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.operator_mission_queue.policy import validate_operator_mission_payload
from k_atlas.core.operator_mission_queue.queue import OperatorMissionQueue


class OperatorMissionQueueSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_operator_mission_queue_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_publish(self) -> None:
        result = validate_operator_mission_payload({
            "title": "Teste",
            "objective": "validar",
            "layer": "social",
            "priority": "high",
            "risk": "high",
            "auto_publish": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("auto_publish_blocked", result["reasons"])

    def test_enqueue_approve_export(self) -> None:
        queue = OperatorMissionQueue(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        mission = queue.enqueue()
        self.assertTrue(mission["ok"])
        self.assertEqual(mission["checkpoint"], "59")
        self.assertEqual(mission["status"], "queued")
        self.assertGreaterEqual(len(mission["tasks"]), 4)

        approval = queue.approve(mission["mission_id"], "tester", "ok")
        self.assertTrue(approval["ok"])
        self.assertEqual(approval["status"], "approved_for_planning")

        export = queue.export_command_center_tasks(mission["mission_id"])
        self.assertTrue(export["ok"])
        self.assertEqual(export["status"], "command_center_payload_created")
        self.assertFalse(export["real_execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_operator_mission_queue.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_operator_mission_queue.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "59")

    def test_export_requires_approval(self) -> None:
        queue = OperatorMissionQueue(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        mission = queue.enqueue()
        export = queue.export_command_center_tasks(mission["mission_id"])
        self.assertFalse(export["ok"])
        self.assertEqual(export["status"], "mission_not_approved_for_planning")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/40_K_Atlas_Operator_Mission_Queue.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
