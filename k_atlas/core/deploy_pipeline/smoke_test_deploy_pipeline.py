from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.deploy_pipeline.pipeline import DeployPipelineAssistant
from k_atlas.core.deploy_pipeline.policy import validate_deploy_payload


class DeployPipelineSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_deploy_pipeline_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_deploy(self) -> None:
        result = validate_deploy_payload({"auto_deploy": True})
        self.assertFalse(result["ok"])
        self.assertIn("auto_deploy_blocked", result["reasons"])

    def test_policy_allows_assisted(self) -> None:
        result = validate_deploy_payload({
            "auto_deploy": False,
            "force_push": False,
            "official_publish": False,
        })
        self.assertTrue(result["ok"])

    def test_run_assisted_check(self) -> None:
        runner = DeployPipelineAssistant(reports_root=self.tmp)
        result = runner.run_assisted_check({
            "target": "render",
            "service": "k-atlas-os",
            "auto_deploy": False,
            "force_push": False,
            "production_mutation": False,
            "official_publish": False,
        })

        self.assertEqual(result["checkpoint"], "39")
        self.assertEqual(result["side_effects"], "report_only_no_deploy")
        self.assertTrue((self.tmp / "latest_deploy_pipeline_report.json").exists())

        loaded = json.loads((self.tmp / "latest_deploy_pipeline_report.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "39")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/20_K_Atlas_Deploy_Pipeline.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
