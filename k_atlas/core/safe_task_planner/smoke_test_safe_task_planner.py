from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.safe_task_planner.planner import SafeTaskPlanner


class SafeTaskPlannerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_safe_planner_"))
        self.planner = SafeTaskPlanner(
            live_dir=self.tmp / "live",
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_plan(self) -> None:
        result = self.planner.create_plan()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "95")
        self.assertFalse(result["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "task_plan_queue.json").exists())

    def test_summary(self) -> None:
        self.planner.create_plan()
        result = self.planner.summary()
        self.assertEqual(result["summary"]["task_plans_total"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/95_K_Atlas_Safe_Task_Planner.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
