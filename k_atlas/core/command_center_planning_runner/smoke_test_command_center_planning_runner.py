from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center_planning_runner.policy import validate_command_center_planning_payload
from k_atlas.core.command_center_planning_runner.runner import CommandCenterPlanningRunner


class CommandCenterPlanningRunnerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_command_center_planning_"))
        command_center_dir = self.tmp / "command_center"

        command_center_dir.mkdir(parents=True, exist_ok=True)

        tasks = [
            {
                "intake_task_id": "task-1",
                "source_task_id": "source-1",
                "mission_id": "mission-1",
                "mission_title": "Missao social",
                "objective": "Criar plano editorial supervisionado do Instagram K-Atlas",
                "layer": "social",
                "risk": "high",
                "status": "queued_for_planning",
                "requires_human_review": True,
            },
            {
                "intake_task_id": "task-2",
                "source_task_id": "source-2",
                "mission_id": "mission-1",
                "mission_title": "Missao social",
                "objective": "Gerar checklist seguro antes de publicacao",
                "layer": "social",
                "risk": "medium",
                "status": "queued_for_planning",
                "requires_human_review": True,
            },
        ]

        (command_center_dir / "mission_intake_queue.json").write_text(
            json.dumps(tasks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.runner = CommandCenterPlanningRunner(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
            command_center_dir=command_center_dir,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_real_execute(self) -> None:
        result = validate_command_center_planning_payload({
            "scope": "all",
            "limit": 25,
            "real_execute": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("real_execute_blocked", result["reasons"])

    def test_run_planning(self) -> None:
        result = self.runner.run({"scope": "all", "limit": 25})

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "61")
        self.assertEqual(result["summary"]["plans_created"], 2)
        self.assertFalse(result["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_command_center_planning_runner.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_command_center_planning_runner.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "61")

    def test_idempotent_run_does_not_duplicate(self) -> None:
        first = self.runner.run({"scope": "all", "limit": 25})
        second = self.runner.run({"scope": "all", "limit": 25})

        self.assertEqual(first["summary"]["plans_created"], 2)
        self.assertEqual(second["summary"]["plans_created"], 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/42_K_Atlas_Command_Center_Planning_Runner.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
