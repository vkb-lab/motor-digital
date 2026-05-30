from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.mission_executor_bridge.bridge import MissionExecutorBridge
from k_atlas.core.mission_executor_bridge.policy import validate_execution_payload
from k_atlas.core.mission_planner.planner import MissionPlanner


class MissionExecutorBridgeSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_mission_executor_"))

        self.command_center = CommandCenter(
            memory_dir=self.tmp / "command_center",
            reports_dir=self.tmp / "command_reports",
        )

        self.planner = MissionPlanner(
            memory_dir=self.tmp / "mission_memory",
            reports_dir=self.tmp / "mission_reports",
            command_center=self.command_center,
        )

        self.bridge = MissionExecutorBridge(
            reports_dir=self.tmp / "bridge_reports",
            memory_dir=self.tmp / "bridge_memory",
            command_center=self.command_center,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_publish(self) -> None:
        result = validate_execution_payload({"auto_publish": True})
        self.assertFalse(result["ok"])
        self.assertIn("auto_publish_blocked", result["reasons"])

    def test_execute_plan_dry_run(self) -> None:
        plan = self.planner.build_plan({
            "title": "Teste executor",
            "mission_type": "system_health",
            "objective": "validar ponte",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
        })

        result = self.bridge.execute_plan(plan=plan, payload={"dry_run": True, "max_tasks": 3})

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "45")
        self.assertTrue((self.tmp / "bridge_reports" / "latest_mission_executor_bridge.json").exists())

        loaded = json.loads((self.tmp / "bridge_reports" / "latest_mission_executor_bridge.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "45")

    def test_blocks_bad_plan(self) -> None:
        result = self.bridge.execute_plan(plan={"ok": False, "tasks": []}, payload={"dry_run": True})
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "mission_plan_not_ready")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/26_K_Atlas_Mission_Executor_Bridge.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
