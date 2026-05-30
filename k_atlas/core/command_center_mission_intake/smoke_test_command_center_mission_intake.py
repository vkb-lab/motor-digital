from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center_mission_intake.intake import CommandCenterMissionIntake
from k_atlas.core.command_center_mission_intake.policy import validate_command_center_intake_payload
from k_atlas.core.operator_mission_queue.queue import OperatorMissionQueue


class CommandCenterMissionIntakeSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_command_center_intake_"))
        self.operator = OperatorMissionQueue(
            reports_dir=self.tmp / "operator_reports",
            memory_dir=self.tmp / "operator_memory",
        )
        self.intake = CommandCenterMissionIntake(
            reports_dir=self.tmp / "intake_reports",
            memory_dir=self.tmp / "intake_memory",
            operator_exports_dir=self.tmp / "operator_memory" / "command_center_exports",
            command_center_dir=self.tmp / "command_center_memory",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_real_execute(self) -> None:
        result = validate_command_center_intake_payload({
            "source": "manual_payload",
            "real_execute": True,
            "tasks": [
                {
                    "objective": "teste",
                }
            ],
        })

        self.assertFalse(result["ok"])
        self.assertIn("real_execute_blocked", result["reasons"])

    def test_manual_intake(self) -> None:
        result = self.intake.intake_payload(self.intake.default_payload())

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "60")
        self.assertEqual(result["tasks_imported"], 1)
        self.assertFalse(result["real_execution_enabled"])
        self.assertTrue((self.tmp / "command_center_memory" / "mission_intake_queue.json").exists())

    def test_process_operator_export(self) -> None:
        mission = self.operator.enqueue()
        self.operator.approve(mission["mission_id"], "tester", "ok")
        export = self.operator.export_command_center_tasks(mission["mission_id"])

        self.assertTrue(export["ok"])

        result = self.intake.process_exports()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "60")
        self.assertGreaterEqual(result["tasks_imported"], 4)
        self.assertFalse(result["real_execution_enabled"])
        self.assertTrue((self.tmp / "intake_reports" / "latest_command_center_mission_intake.json").exists())

        loaded = json.loads((self.tmp / "intake_reports" / "latest_command_center_mission_intake.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "60")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/41_K_Atlas_Command_Center_Mission_Intake.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
