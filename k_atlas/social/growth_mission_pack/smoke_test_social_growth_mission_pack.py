from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.command_center.center import CommandCenter
from k_atlas.core.mission_planner.planner import MissionPlanner
from k_atlas.social.growth_mission_pack.pack import SocialGrowthMissionPack
from k_atlas.social.growth_mission_pack.policy import validate_social_growth_payload


class SocialGrowthMissionPackSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_social_growth_pack_"))
        self.command_center = CommandCenter(
            memory_dir=self.tmp / "command_center",
            reports_dir=self.tmp / "command_reports",
        )
        self.mission_planner = MissionPlanner(
            memory_dir=self.tmp / "mission_memory",
            reports_dir=self.tmp / "mission_reports",
            command_center=self.command_center,
        )
        self.pack = SocialGrowthMissionPack(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
            mission_planner=self.mission_planner,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_publish(self) -> None:
        payload = self.pack.default_payload()
        payload["auto_publish"] = True
        result = validate_social_growth_payload(payload)
        self.assertFalse(result["ok"])
        self.assertIn("auto_publish_blocked", result["reasons"])

    def test_generate_pack(self) -> None:
        result = self.pack.generate(enqueue_mission=True)
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "46")
        self.assertEqual(len(result["calendar"]), 7)
        self.assertTrue((self.tmp / "reports" / "latest_social_growth_mission_pack.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_social_growth_mission_pack.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "46")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/27_K_Atlas_Social_Growth_Mission_Pack.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
