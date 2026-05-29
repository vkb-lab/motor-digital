from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.control_plane.event_bus import EventBus
from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue
from k_atlas.core.control_plane.task_router import TaskRouter
from k_atlas.core.supervisor_autopilot.autopilot import SupervisorAutopilot
from k_atlas.core.supervisor_autopilot.policy import AutopilotPolicy


class SupervisorAutopilotSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_autopilot_"))
        self.event_bus = EventBus(self.tmp / "events.jsonl")
        self.queue = SupervisorQueue(self.tmp / "supervisor_queue.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def route(self, action: str, payload: dict) -> None:
        router = TaskRouter(
            event_bus=self.event_bus,
            supervisor_queue=self.queue,
        )
        router.route(
            objective=f"Teste {action}",
            agent_id="k_social_operator",
            action=action,
            payload=payload,
            requested_by="smoke_test",
        )

    def test_policy_allows_safe_content_package(self) -> None:
        self.route("create_content_package", {
            "module": "k_atlas",
            "official_publish": False,
            "external_api_enabled": False,
        })

        item = self.queue.load()[0]
        decision = AutopilotPolicy().evaluate(item)

        self.assertTrue(decision.ok)

    def test_policy_blocks_official_publish(self) -> None:
        self.route("official_publish", {
            "official_publish": True,
        })

        item = self.queue.load()[0]
        decision = AutopilotPolicy().evaluate(item)

        self.assertFalse(decision.ok)

    def test_autopilot_approves_safe_task(self) -> None:
        self.route("create_content_package", {
            "module": "k_atlas",
            "official_publish": False,
            "external_api_enabled": False,
        })

        autopilot = SupervisorAutopilot(
            supervisor_queue=self.queue,
            event_bus=self.event_bus,
            run_log_path=self.tmp / "autopilot_runs.json",
        )

        result = autopilot.run_once()

        self.assertEqual(result["approved_count"], 1)
        self.assertEqual(result["blocked_count"], 0)
        self.assertEqual(self.queue.load()[0]["status"], "approved")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/15_K_Atlas_Supervisor_Autopilot.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
