from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.assisted_autonomy.orchestrator import AssistedAutonomyOrchestrator
from k_atlas.core.assisted_autonomy.policy import validate_autonomy_payload


class AssistedAutonomySmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_assisted_autonomy_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_deploy(self) -> None:
        result = validate_autonomy_payload({"auto_deploy": True})
        self.assertFalse(result["ok"])
        self.assertIn("auto_deploy_blocked", result["reasons"])

    def test_policy_allows_safe_payload(self) -> None:
        result = validate_autonomy_payload({
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_enabled": False,
            "mass_messaging": False,
            "browser_automation": False,
        })
        self.assertTrue(result["ok"])

    def test_orchestrator_generates_report_without_deep_checks(self) -> None:
        runner = AssistedAutonomyOrchestrator(reports_root=self.tmp)
        result = runner.run({
            "mode": "assisted_autonomy_v1",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_enabled": False,
            "mass_messaging": False,
            "browser_automation": False,
            "run_deep_checks": False,
        }, requested_by="smoke_test")

        self.assertEqual(result["checkpoint"], "40")
        self.assertTrue((self.tmp / "k_atlas_assisted_autonomy_v1.json").exists())
        self.assertTrue((self.tmp / "k_atlas_assisted_autonomy_v1.md").exists())

        loaded = json.loads((self.tmp / "k_atlas_assisted_autonomy_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "40")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/21_K_Atlas_Assisted_Autonomy.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
