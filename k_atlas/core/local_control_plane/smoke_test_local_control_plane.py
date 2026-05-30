from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_control_plane.control_plane import KAtlasLocalControlPlane
from k_atlas.core.local_control_plane.policy import validate_control_plane_request


class KAtlasLocalControlPlaneSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_local_control_plane_"))

        modules = [
            "k_atlas/core/autoprogramming_cycle_dashboard",
            "k_atlas/core/autoprogramming_cycle_controller",
            "k_atlas/core/local_mission_installer",
            "k_atlas/core/mission_pack_generator",
            "k_atlas/core/mission_pack_bridge",
            "k_atlas/core/mission_pipeline_runner",
        ]

        for item in modules:
            (self.tmp / item).mkdir(parents=True, exist_ok=True)

        pages = [
            "pages/71_K_Atlas_Autoprogramming_Cycle_Dashboard.py",
            "pages/72_K_Atlas_Autoprogramming_Cycle_Controller.py",
            "pages/73_K_Atlas_Local_Mission_Installer.py",
            "pages/74_K_Atlas_Mission_Pack_Generator.py",
            "pages/75_K_Atlas_Mission_Pack_Bridge.py",
            "pages/76_K_Atlas_Mission_Pipeline_Runner.py",
        ]

        for item in pages:
            target = self.tmp / item
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("demo", encoding="utf-8")

        queues = {
            "live/autoprogramming_cycle_controller/cycle_decision_queue.json": [{"id": 1}],
            "live/mission_pack_generator/mission_pack_queue.json": [{"id": 1}],
            "live/mission_pack_bridge/local_mission_queue.json": [{"id": 1}],
            "live/local_mission_installer/local_mission_queue.json": [{"id": 1}],
            "live/mission_pipeline_runner/pipeline_runs.json": [{"id": 1}],
            "memory/local_mission_installer/install_manifest.json": [{"id": 1}],
        }

        for path, data in queues.items():
            target = self.tmp / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data), encoding="utf-8")

        self.control_plane = KAtlasLocalControlPlane(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_remote_control(self) -> None:
        result = validate_control_plane_request({
            "mode": "observe",
            "remote_control_enabled": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("remote_control_enabled_blocked", result["reasons"])

    def test_build_report(self) -> None:
        report = self.control_plane.build_report({"mode": "recommend"})

        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "77")
        self.assertEqual(report["summary"]["modules_ready"], 6)
        self.assertTrue(report["summary"]["control_plane_ready"])
        self.assertFalse(report["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "local_control_plane" / "control_plane_state.json").exists())

    def test_report_files_created(self) -> None:
        self.control_plane.build_report({"mode": "observe"})

        self.assertTrue((self.tmp / "reports" / "local_control_plane" / "latest_local_control_plane.json").exists())
        self.assertTrue((self.tmp / "reports" / "local_control_plane" / "latest_local_control_plane.md").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/77_K_Atlas_Local_Control_Plane.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
