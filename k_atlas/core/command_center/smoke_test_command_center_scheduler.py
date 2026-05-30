from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.command_center.scheduler import CommandCenterScheduler


class CommandCenterSchedulerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_command_scheduler_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scheduler_run_once_without_execution(self) -> None:
        center = CommandCenter(
            memory_dir=self.tmp / "command_center",
            reports_dir=self.tmp / "reports",
        )
        scheduler = CommandCenterScheduler(
            state_dir=self.tmp / "scheduler",
            command_center=center,
            interval_seconds=30,
        )

        result = scheduler.run_once("teste scheduler", execute_tasks=False)

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "43")
        self.assertTrue((self.tmp / "scheduler" / "scheduler_state.json").exists())

    def test_scheduler_state_can_load(self) -> None:
        center = CommandCenter(
            memory_dir=self.tmp / "command_center",
            reports_dir=self.tmp / "reports",
        )
        scheduler = CommandCenterScheduler(
            state_dir=self.tmp / "scheduler",
            command_center=center,
            interval_seconds=30,
        )

        scheduler.run_once("teste scheduler", execute_tasks=False)
        state = scheduler.load_state()

        self.assertEqual(state["checkpoint"], "43")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/24_K_Atlas_Command_Scheduler.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
