from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_mission_installer.policy import validate_mission_package
from k_atlas.core.mission_pack_generator.generator import MissionPackGenerator
from k_atlas.core.mission_pack_bridge.bridge import MissionPackBridge


class MissionPackBridgeSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_mission_pack_bridge_"))
        self.generator = MissionPackGenerator(project_root=self.tmp)
        self.bridge = MissionPackBridge(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_bridge_latest_pack(self) -> None:
        self.generator.generate_pack(
            objective="Criar relatorio seguro",
            target_path="reports/autoprog_generated/bridge_safe.md",
        )

        report = self.bridge.bridge_latest()

        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "75")
        self.assertEqual(report["status"], "local_mission_generated")
        self.assertTrue((self.tmp / "live" / "mission_pack_bridge" / "latest_local_mission.kmission.json").exists())

        local = json.loads((self.tmp / "live" / "mission_pack_bridge" / "latest_local_mission.kmission.json").read_text(encoding="utf-8"))
        validation = validate_mission_package(local)

        self.assertTrue(validation["ok"])
        self.assertEqual(local["schema_version"], "k_atlas.local_mission.v1")
        self.assertFalse(local["auto_execute"])
        self.assertFalse(local["real_execution_enabled"])
        self.assertEqual(local["steps"][0]["path"], "reports/autoprog_generated/bridge_safe.md")

    def test_missing_pack_blocks(self) -> None:
        report = self.bridge.bridge_latest()
        self.assertFalse(report["ok"])
        self.assertEqual(report["status"], "source_pack_not_found_or_invalid_json")

    def test_summary(self) -> None:
        self.generator.generate_pack(
            objective="Criar resumo seguro",
            target_path="reports/autoprog_generated/bridge_summary.md",
        )
        self.bridge.bridge_latest()
        summary = self.bridge.summary()

        self.assertTrue(summary["ok"])
        self.assertEqual(summary["summary"]["generated_local_missions_total"], 1)
        self.assertTrue(summary["summary"]["latest_local_mission_exists"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/75_K_Atlas_Mission_Pack_Bridge.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
