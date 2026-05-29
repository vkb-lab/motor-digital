# -*- coding: utf-8 -*-
"""Smoke tests for K-Social human approval queue."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.audit.social_approval_queue import SocialApprovalQueue


def build_valid_operation() -> dict:
    return {
        "system": "K-Social Intelligence System",
        "operation_status": "draft_ready_for_human_review",
        "human_review_required": True,
        "publication_permission": False,
        "external_api_used": False,
        "audience": {
            "product": "BRICS Paraguay Autos",
            "market": "marketplace automotivo Paraguai-Brasil",
            "segments": [
                {"persona": "compradores brasileiros interessados em carros no Paraguai"}
            ],
        },
        "creative_brief": {
            "product": "BRICS Paraguay Autos",
            "objective": "validar campanha supervisionada",
        },
        "campaign": {
            "objective": "validar campanha supervisionada",
            "channels": ["Instagram", "Facebook", "WhatsApp"],
            "duration_days": 5,
            "content_calendar": [
                {"day": 1, "channel": "Instagram", "publish_automatically": False},
                {"day": 1, "channel": "Facebook", "publish_automatically": False},
                {"day": 1, "channel": "WhatsApp", "publish_automatically": False},
            ],
        },
        "audit": {
            "audit_status": "approved_for_human_review",
            "errors": [],
            "warnings": [],
            "human_review_required": True,
            "publication_permission": False,
            "approved_for_auto_publish": False,
        },
        "request_metadata": {
            "approval_status": "pending_human_review",
        },
    }


class TestSocialApprovalQueue(unittest.TestCase):
    """Validates human approval queue behavior."""

    def test_queue_builds_and_updates_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            reports_dir = base_dir / "reports"
            memory_dir = base_dir / "memory"
            reports_dir.mkdir(parents=True, exist_ok=True)
            memory_dir.mkdir(parents=True, exist_ok=True)

            operation_path = reports_dir / "operation_test.json"
            operation_path.write_text(
                json.dumps(build_valid_operation(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            queue_manager = SocialApprovalQueue(
                reports_dir=reports_dir,
                memory_dir=memory_dir,
            )

            queue = queue_manager.save_queue()

            self.assertEqual(queue["total_items"], 1)
            self.assertEqual(queue["counts"]["pending_human_review"], 1)
            self.assertFalse(queue["publication_permission"])
            self.assertFalse(queue["approved_for_auto_publish"])
            self.assertTrue((memory_dir / "social_approval_queue.json").exists())

            updated_queue = queue_manager.update_decision(
                source_file="operation_test.json",
                decision="needs_revision",
                reviewer="K-Atlas Operator",
                notes="Ajustar mensagem antes de seguir.",
            )

            self.assertEqual(updated_queue["counts"]["needs_revision"], 1)
            self.assertEqual(updated_queue["counts"]["pending_human_review"], 0)

            updated_operation = json.loads(
                operation_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                updated_operation["request_metadata"]["approval_status"],
                "needs_revision",
            )
            self.assertFalse(updated_operation["publication_permission"])
            self.assertTrue(updated_operation["human_review_required"])
            self.assertEqual(len(updated_operation["approval_events"]), 1)

    def test_queue_rejects_invalid_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue_manager = SocialApprovalQueue(
                reports_dir=Path(temp_dir) / "reports",
                memory_dir=Path(temp_dir) / "memory",
            )

            with self.assertRaises(ValueError):
                queue_manager.update_decision(
                    source_file="missing.json",
                    decision="approved_for_auto_publish",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
