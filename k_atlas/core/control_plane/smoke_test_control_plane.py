from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.control_plane.agent_registry import build_default_agent_registry
from k_atlas.core.control_plane.autonomy_policy import AutonomyPolicy, ControlDecision
from k_atlas.core.control_plane.event_bus import EventBus
from k_atlas.core.control_plane.health_check import run_control_plane_health_check
from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue
from k_atlas.core.control_plane.task_router import TaskRouter


class ControlPlaneSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_control_plane_"))
        self.event_bus = EventBus(self.tmp / "events.jsonl")
        self.supervisor_queue = SupervisorQueue(self.tmp / "supervisor_queue.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_agents_registered(self) -> None:
        registry = build_default_agent_registry()
        agents = registry.to_dict()

        self.assertIn("k_social_operator", agents)
        self.assertIn("k_saas_builder", agents)
        self.assertIn("k_supervisor", agents)

    def test_policy_blocks_plaintext_secret(self) -> None:
        registry = build_default_agent_registry()
        agent = registry.get("k_social_operator")
        result = AutonomyPolicy().evaluate(
            agent=agent,
            action="create_campaign",
            payload={"access_token": "plain-text"},
        )

        self.assertEqual(result.decision, ControlDecision.DENY)
        self.assertTrue(any("plaintext_secret_blocked" in reason for reason in result.reasons))

    def test_router_sends_supervised_task_to_approval_queue(self) -> None:
        router = TaskRouter(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
        )

        result = router.route(
            objective="Criar pacote de midia digital",
            agent_id="k_social_operator",
            action="create_content_package",
            payload={"campaign_id": "generic-campaign"},
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.status, "pending_approval")

        approvals = self.supervisor_queue.load()
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0]["status"], "pending_approval")

    def test_router_denies_blocked_action(self) -> None:
        router = TaskRouter(
            event_bus=self.event_bus,
            supervisor_queue=self.supervisor_queue,
        )

        result = router.route(
            objective="Publicar sem aprovacao",
            agent_id="k_social_operator",
            action="official_publish",
            payload={"official_publish": True},
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.status, "denied")

    def test_event_bus_writes_events(self) -> None:
        event = self.event_bus.emit(
            event_type="system.test",
            source="smoke_test",
            payload={"ok": True},
        )

        self.assertEqual(event["event_type"], "system.test")
        events = self.event_bus.read_events()
        self.assertEqual(len(events), 1)

    def test_health_check(self) -> None:
        result = run_control_plane_health_check()

        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["agents_registered"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)