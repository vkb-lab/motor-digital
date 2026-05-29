from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.control_plane.event_bus import EventBus
from k_atlas.core.control_plane.executor import ControlPlaneExecutor
from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue
from k_atlas.core.control_plane.task_router import TaskRouter


class ControlPlaneExecutorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_executor_"))
        self.event_bus = EventBus(self.tmp / "events.jsonl")
        self.supervisor_queue = SupervisorQueue(self.tmp / "supervisor_queue.json")
        self.executor = ControlPlaneExecutor(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
            output_dir=self.tmp / "executions",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def create_approved_task(self, action: str = "create_content_package") -> str:
        router = TaskRouter(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
        )

        result = router.route(
            objective="Executar tarefa supervisionada",
            agent_id="k_social_operator",
            action=action,
            payload={"module": "k_atlas", "risk": "controlled", "official_publish": False},
            requested_by="smoke_test",
        )

        self.assertEqual(result.status, "pending_approval")

        approval_id = self.supervisor_queue.load()[0]["approval_id"]
        self.supervisor_queue.approve(approval_id, reviewer="k_supervisor")
        return approval_id

    def test_execute_approved_content_package(self) -> None:
        approval_id = self.create_approved_task("create_content_package")
        result = self.executor.execute_approved(approval_id)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["action"], "create_content_package")
        self.assertTrue(Path(result["output_path"]).exists())

    def test_execute_all_approved(self) -> None:
        self.create_approved_task("create_content_package")
        results = self.executor.execute_all_approved()

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["ok"])

    def test_blocks_unapproved_task(self) -> None:
        router = TaskRouter(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
        )

        router.route(
            objective="Criar tarefa sem aprovar",
            agent_id="k_social_operator",
            action="create_content_package",
            payload={"module": "k_atlas"},
            requested_by="smoke_test",
        )

        approval_id = self.supervisor_queue.load()[0]["approval_id"]
        result = self.executor.execute_approved(approval_id)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "not_approved")

    def test_run_smoke_test_safe_action(self) -> None:
        router = TaskRouter(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
        )

        result = router.route(
            objective="Rodar smoke test seguro",
            agent_id="k_saas_builder",
            action="run_smoke_test",
            payload={"module": "control_plane"},
            requested_by="smoke_test",
        )

        self.assertEqual(result.status, "pending_approval")

        approval_id = self.supervisor_queue.load()[0]["approval_id"]
        self.supervisor_queue.approve(approval_id, reviewer="k_supervisor")

        execution = self.executor.execute_approved(approval_id)

        self.assertTrue(execution["ok"])
        self.assertEqual(execution["data"]["status"], "passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)