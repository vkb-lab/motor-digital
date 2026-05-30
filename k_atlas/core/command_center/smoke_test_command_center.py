from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.command_center.policy import validate_command_payload


class CommandCenterSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_command_center_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_publish(self) -> None:
        result = validate_command_payload({"action": "health_check", "official_publish": True})
        self.assertFalse(result["ok"])

    def test_create_cycle(self) -> None:
        center = CommandCenter(memory_dir=self.tmp / "memory", reports_dir=self.tmp / "reports")
        result = center.create_cycle("teste")
        self.assertTrue(result["ok"])
        self.assertTrue((self.tmp / "memory" / "command_queue.json").exists())

    def test_run_pending_once(self) -> None:
        center = CommandCenter(memory_dir=self.tmp / "memory", reports_dir=self.tmp / "reports")
        center.create_cycle("teste")
        report = center.run_pending_once(limit=1)
        self.assertEqual(report["checkpoint"], "42")
        self.assertEqual(report["executed_count"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/23_K_Atlas_Command_Center.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
