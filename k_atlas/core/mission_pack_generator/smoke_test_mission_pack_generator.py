from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.mission_pack_generator.generator import MissionPackGenerator
from k_atlas.core.mission_pack_generator.policy import validate_mission_pack, validate_mission_step


class MissionPackGeneratorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_mission_pack_generator_"))
        self.generator = MissionPackGenerator(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_step_blocks_external_path(self) -> None:
        result = validate_mission_step({
            "action": "write_file",
            "path": "secrets/token.txt",
            "content": "demo",
        })

        self.assertFalse(result["ok"])
        self.assertIn("path_prefix_not_allowed:secrets/token.txt", result["reasons"])

    def test_pack_blocks_auto_execution(self) -> None:
        result = validate_mission_pack({
            "mission_pack_id": "pack",
            "mission_id": "mission",
            "objective": "demo",
            "auto_execute": True,
            "steps": [
                {
                    "action": "write_file",
                    "path": "reports/autoprog_generated/demo.md",
                    "content": "demo",
                }
            ],
        })

        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_generate_pack(self) -> None:
        report = self.generator.generate_pack(
            objective="Criar arquivo seguro",
            target_path="reports/autoprog_generated/safe.md",
        )

        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "74")
        self.assertEqual(report["status"], "mission_pack_generated")
        self.assertTrue((self.tmp / "live" / "mission_pack_generator" / "latest_mission_pack.json").exists())
        self.assertTrue((self.tmp / "reports" / "mission_pack_generator" / "latest_mission_pack_generator.json").exists())

        latest = json.loads((self.tmp / "live" / "mission_pack_generator" / "latest_mission_pack.json").read_text(encoding="utf-8"))
        self.assertFalse(latest["automatic_execution_allowed"])
        self.assertTrue(latest["human_approval_required"])
        self.assertEqual(latest["steps"][0]["path"], "reports/autoprog_generated/safe.md")

    def test_summary(self) -> None:
        self.generator.generate_pack(
            objective="Criar resumo seguro",
            target_path="reports/autoprog_generated/summary.md",
        )
        summary = self.generator.summary()

        self.assertTrue(summary["ok"])
        self.assertEqual(summary["summary"]["generated_packs_total"], 1)
        self.assertTrue(summary["summary"]["latest_pack_exists"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/74_K_Atlas_Mission_Pack_Generator.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
