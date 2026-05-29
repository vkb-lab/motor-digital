from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.control_plane.event_bus import EventBus
from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue
from k_atlas.core.workflows.workflow_definitions import build_default_workflows, get_workflow
from k_atlas.core.workflows.workflow_runner import AgentWorkflowRunner, WorkflowRunStore


class AgentWorkflowsSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_workflows_"))
        self.event_bus = EventBus(self.tmp / "events.jsonl")
        self.supervisor_queue = SupervisorQueue(self.tmp / "supervisor_queue.json")
        self.run_store = WorkflowRunStore(self.tmp / "workflow_runs.json")
        self.runner = AgentWorkflowRunner(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
            run_store=self.run_store,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_workflows_exist(self) -> None:
        workflows = build_default_workflows()

        expected = {
            "control_plane_report",
            "social_content_package",
            "saas_mvp_bootstrap",
            "deploy_readiness",
            "creative_media_package",
        }

        self.assertTrue(expected.issubset(set(workflows.keys())))

    def test_get_workflow(self) -> None:
        workflow = get_workflow("social_content_package")

        self.assertEqual(workflow.workflow_id, "social_content_package")
        self.assertGreaterEqual(len(workflow.steps), 1)

    def test_social_workflow_creates_pending_approvals(self) -> None:
        result = self.runner.run_workflow(
            workflow_id="social_content_package",
            workflow_input={"objective": "testar midia digital"},
            requested_by="smoke_test",
        )

        self.assertEqual(result["status"], "pending_supervision")

        approvals = self.supervisor_queue.load()
        self.assertGreaterEqual(len(approvals), 1)
        self.assertTrue(
            all(item["status"] == "pending_approval" for item in approvals)
        )

    def test_control_plane_report_workflow_routes_all_steps(self) -> None:
        result = self.runner.run_workflow(
            workflow_id="control_plane_report",
            workflow_input={"objective": "gerar relatorio"},
            requested_by="smoke_test",
        )

        self.assertIn(result["status"], {"allowed", "pending_supervision", "partially_denied"})
        self.assertEqual(result["summary"]["steps_total"], 3)

        denied = result["summary"]["steps_denied"]
        self.assertEqual(denied, 0)

    def test_deploy_readiness_workflow_is_persisted(self) -> None:
        result = self.runner.run_workflow(
            workflow_id="deploy_readiness",
            workflow_input={"objective": "validar deploy"},
            requested_by="smoke_test",
        )

        self.assertIn(result["status"], {"pending_supervision", "allowed"})
        self.assertEqual(result["summary"]["steps_denied"], 0)

        runs = self.run_store.load()

        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["workflow_id"], "deploy_readiness")

    def test_creative_media_workflow_routes_without_denial(self) -> None:
        result = self.runner.run_workflow(
            workflow_id="creative_media_package",
            workflow_input={"objective": "preparar pacote criativo generico"},
            requested_by="smoke_test",
        )

        self.assertIn(result["status"], {"pending_supervision", "allowed"})
        self.assertEqual(result["summary"]["steps_denied"], 0)

    def test_page_compiles(self) -> None:
        self.assertTrue(Path("pages/10_K_Atlas_Workflows.py").exists())
        py_compile.compile("pages/10_K_Atlas_Workflows.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)