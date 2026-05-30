from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.supervised_autonomy_queue.queue import SupervisedAutonomyQueue


class SupervisedAutonomyQueueSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_supervised_queue_"))
        self.plan_queue = self.tmp / "plans.json"
        self.plan_queue.write_text(json.dumps([{"plan_id": "plan-1", "goal": "demo"}]), encoding="utf-8")
        self.queue = SupervisedAutonomyQueue(
            plan_queue_path=self.plan_queue,
            live_dir=self.tmp / "live",
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_queue(self) -> None:
        result = self.queue.build_queue()
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["created_items"], 1)
        self.assertFalse(result["summary"]["real_execution_enabled"])

    def test_idempotent(self) -> None:
        first = self.queue.build_queue()
        second = self.queue.build_queue()
        self.assertEqual(first["summary"]["created_items"], 1)
        self.assertEqual(second["summary"]["created_items"], 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/96_K_Atlas_Supervised_Autonomy_Queue.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
