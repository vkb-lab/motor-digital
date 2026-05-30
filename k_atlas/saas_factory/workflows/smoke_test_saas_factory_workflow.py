from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.saas_factory.workflows.factory_workflow import SaaSFactoryWorkflowRunner
from k_atlas.saas_factory.workflows.workflow_spec import build_default_saas_workflow_payload, validate_saas_workflow_payload


class SaaSFactoryWorkflowSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_saas_workflow_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_payload_validates(self) -> None:
        payload = build_default_saas_workflow_payload()
        validation = validate_saas_workflow_payload(payload)

        self.assertTrue(validation["ok"])

    def test_blocks_auto_deploy(self) -> None:
        payload = build_default_saas_workflow_payload()
        payload["auto_deploy"] = True

        validation = validate_saas_workflow_payload(payload)

        self.assertFalse(validation["ok"])
        self.assertIn("auto_deploy_blocked", validation["reasons"])

    def test_workflow_runs_and_generates_product(self) -> None:
        runner = SaaSFactoryWorkflowRunner(
            products_root=self.tmp / "products",
            reports_root=self.tmp / "reports",
        )

        result = runner.run(
            payload=build_default_saas_workflow_payload(),
            requested_by="smoke_test",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "38")
        self.assertTrue(Path(result["product_dir"]).exists())
        self.assertTrue((Path(result["product_dir"]) / "deploy_plan.json").exists())
        self.assertTrue((self.tmp / "reports" / "latest_saas_factory_workflow.json").exists())

    def test_report_can_be_loaded(self) -> None:
        runner = SaaSFactoryWorkflowRunner(
            products_root=self.tmp / "products",
            reports_root=self.tmp / "reports",
        )

        result = runner.run(build_default_saas_workflow_payload(), requested_by="smoke_test")
        latest = self.tmp / "reports" / "latest_saas_factory_workflow.json"

        loaded = json.loads(latest.read_text(encoding="utf-8"))

        self.assertEqual(loaded["workflow_id"], result["workflow_id"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/19_K_Atlas_SaaS_Factory_Workflow.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
