from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.mission_pipeline_runner.policy import validate_pipeline_request
from k_atlas.core.mission_pipeline_runner.runner import MissionPipelineRunner


class MissionPipelineRunnerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_mission_pipeline_"))

        required_dirs = [
            "k_atlas/core/mission_pack_generator",
            "k_atlas/core/mission_pack_bridge",
            "k_atlas/core/local_mission_installer",
        ]

        for item in required_dirs:
            (self.tmp / item).mkdir(parents=True, exist_ok=True)

        required_files = [
            "pages/74_K_Atlas_Mission_Pack_Generator.py",
            "pages/75_K_Atlas_Mission_Pack_Bridge.py",
            "pages/73_K_Atlas_Local_Mission_Installer.py",
            "ops/run_mission_pack_generator_demo.ps1",
            "ops/run_mission_pack_bridge_demo.ps1",
            "ops/install_local_mission.ps1",
        ]

        for item in required_files:
            target = self.tmp / item
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("demo", encoding="utf-8")

        self.runner = MissionPipelineRunner(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_execute(self) -> None:
        result = validate_pipeline_request({
            "mode": "dry_run",
            "auto_execute": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_policy_requires_human_approval_for_install(self) -> None:
        result = validate_pipeline_request({
            "mode": "supervised",
            "install": True,
            "human_approved": False,
        })

        self.assertFalse(result["ok"])
        self.assertIn("human_approval_required_for_install", result["reasons"])

    def test_build_plan(self) -> None:
        plan = self.runner.build_plan()

        self.assertTrue(plan["ok"])
        self.assertEqual(len(plan["steps"]), 3)
        self.assertFalse(plan["real_execution_enabled"])

    def test_dry_run(self) -> None:
        report = self.runner.dry_run({"mode": "dry_run"})

        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "76")
        self.assertEqual(report["summary"]["steps_ready"], 3)
        self.assertFalse(report["summary"]["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/76_K_Atlas_Mission_Pipeline_Runner.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
