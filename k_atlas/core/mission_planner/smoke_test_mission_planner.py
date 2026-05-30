from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.mission_planner.planner import MissionPlanner
from k_atlas.core.mission_planner.policy import validate_mission_payload


class MissionPlannerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_mission_planner_"))
        self.command_center = CommandCenter(
            memory_dir=self.tmp / "command_center",
            reports_dir=self.tmp / "command_reports",
        )
        self.planner = MissionPlanner(
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
            command_center=self.command_center,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_deploy(self) -> None:
        result = validate_mission_payload({
            "title": "Teste",
            "mission_type": "daily_operator",
            "auto_deploy": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("auto_deploy_blocked", result["reasons"])

    def test_build_plan(self) -> None:
        result = self.planner.build_plan({
            "title": "Teste",
            "mission_type": "daily_operator",
            "objective": "validar sistema",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "44")
        self.assertGreater(len(result["tasks"]), 0)
        self.assertTrue((self.tmp / "reports" / "latest_mission_plan.json").exists())

    def test_plan_and_enqueue(self) -> None:
        result = self.planner.plan_and_enqueue({
            "title": "Teste",
            "mission_type": "system_health",
            "objective": "validar saude",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
        })

        self.assertTrue(result["ok"])
        queue = json.loads((self.tmp / "command_center" / "command_queue.json").read_text(encoding="utf-8"))
        self.assertGreater(len(queue), 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/25_K_Atlas_Mission_Planner.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
