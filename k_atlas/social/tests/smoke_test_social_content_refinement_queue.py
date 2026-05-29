# -*- coding: utf-8 -*-
"""Smoke tests for K-Social content refinement queue."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.creative_engine.social_content_refinement_queue import (
    SocialContentRefinementQueue,
)


def build_operation(approval_status: str) -> dict:
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
            "approval_status": approval_status,
            "last_review_notes": "Ajustar linguagem antes de refinamento criativo.",
        },
    }


class TestSocialContentRefinementQueue(unittest.TestCase):
    """Validates content refinement queue generation."""

    def test_queue_builds_tasks_for_needs_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            reports_dir = base_dir / "reports"
            memory_dir = base_dir / "memory"
            reports_dir.mkdir(parents=True, exist_ok=True)
            memory_dir.mkdir(parents=True, exist_ok=True)

            operation_path = reports_dir / "operation_needs_revision.json"
            operation_path.write_text(
                json.dumps(build_operation("needs_revision"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            queue_manager = SocialContentRefinementQueue(
                reports_dir=reports_dir,
                memory_dir=memory_dir,
            )

            queue = queue_manager.save_queue()

            self.assertEqual(queue["total_tasks"], 5)
            self.assertEqual(queue["counts"]["pending_refinement"], 5)
            self.assertFalse(queue["publication_permission"])
            self.assertFalse(queue["approved_for_auto_publish"])
            self.assertTrue((memory_dir / "social_content_refinement_queue.json").exists())

            task_types = {task["task_type"] for task in queue["tasks"]}

            self.assertIn("caption_refinement", task_types)
            self.assertIn("hook_variations", task_types)
            self.assertIn("reel_script", task_types)
            self.assertIn("ai_image_prompt", task_types)
            self.assertIn("ai_video_prompt", task_types)

    def test_queue_ignores_pending_operations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            reports_dir = base_dir / "reports"
            memory_dir = base_dir / "memory"
            reports_dir.mkdir(parents=True, exist_ok=True)
            memory_dir.mkdir(parents=True, exist_ok=True)

            operation_path = reports_dir / "operation_pending.json"
            operation_path.write_text(
                json.dumps(build_operation("pending_human_review"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            queue_manager = SocialContentRefinementQueue(
                reports_dir=reports_dir,
                memory_dir=memory_dir,
            )

            queue = queue_manager.save_queue()

            self.assertEqual(queue["total_tasks"], 0)
            self.assertEqual(queue["counts"]["pending_refinement"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
