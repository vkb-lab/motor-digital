from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_mission_installer.installer import LocalMissionInstaller
from k_atlas.core.local_mission_installer.policy import (
    sha256_text,
    validate_manual_install_request,
    validate_mission_package,
)


class LocalMissionInstallerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_local_mission_"))
        self.installer = LocalMissionInstaller(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def mission(self) -> dict:
        content = "# Demo\n"
        return {
            "schema_version": "k_atlas.local_mission.v1",
            "mission_id": "mission-1",
            "mission_name": "Demo",
            "status": "draft_ready_for_local_review",
            "install_mode": "manual_only",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
            "steps": [
                {
                    "action": "write_file",
                    "path": "k_atlas/core/demo_local_mission/README.md",
                    "content": content,
                    "content_sha256": sha256_text(content),
                }
            ],
        }

    def test_policy_blocks_auto_execute(self) -> None:
        data = self.mission()
        data["auto_execute"] = True
        result = validate_mission_package(data)

        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_policy_blocks_shell_step(self) -> None:
        data = self.mission()
        data["steps"][0]["action"] = "run_shell"
        result = validate_mission_package(data)

        self.assertFalse(result["ok"])
        self.assertIn("invalid_step_detected", result["reasons"])

    def test_request_requires_human_approval(self) -> None:
        result = validate_manual_install_request({
            "human_approved": False,
            "install_mode": "manual",
        })

        self.assertFalse(result["ok"])
        self.assertIn("human_approval_required", result["reasons"])

    def test_import_approve_dry_run_install(self) -> None:
        imported = self.installer.import_mission_package(self.mission())
        self.assertTrue(imported["ok"])

        approved = self.installer.approve_mission("mission-1", "tester", "ok")
        self.assertTrue(approved["ok"])

        dry = self.installer.dry_run("mission-1")
        self.assertTrue(dry["ok"])
        self.assertEqual(dry["summary"]["planned_steps"], 1)

        installed = self.installer.install_manual({
            "human_approved": True,
            "install_mode": "manual",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        }, "mission-1")

        self.assertTrue(installed["ok"])
        self.assertEqual(installed["status"], "manual_install_completed")
        self.assertTrue((self.tmp / "k_atlas" / "core" / "demo_local_mission" / "README.md").exists())
        self.assertTrue((self.tmp / "memory" / "local_mission_installer" / "install_manifest.json").exists())

    def test_demo_mission_file(self) -> None:
        demo = self.installer.build_demo_mission()
        self.assertTrue(Path(demo["mission_path"]).exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/73_K_Atlas_Local_Mission_Installer.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
