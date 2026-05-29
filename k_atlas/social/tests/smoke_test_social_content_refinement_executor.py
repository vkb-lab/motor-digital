# -*- coding: utf-8 -*-
"""Smoke tests for K-Social content refinement executor."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.creative_engine.social_content_refinement_executor import (
    SocialContentRefinementExecutor,
)


class TestSocialContentRefinementExecutor(unittest.TestCase):
    """Validates local execution of refinement tasks."""

    def test_executor_generates_markdown_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            queue_file = base_dir / "social_content_refinement_queue.json"
            output_dir = base_dir / "outputs"

            queue = {
                "system": "K-Social Content Refinement Queue",
                "total_tasks": 2,
                "publication_permission": False,
                "external_api_used": False,
                "human_review_required": True,
                "approved_for_auto_publish": False,
                "tasks": [
                    {
                        "task_id": "task_01",
                        "status": "pending_refinement",
                        "task_type": "caption_refinement",
                        "title": "Refinar legenda principal",
                        "product": "BRICS Paraguay Autos",
                        "objective": "validar campanha",
                        "approval_status": "needs_revision",
                        "review_notes": "Ajustar linguagem.",
                        "channels": ["Instagram", "Facebook"],
                        "instructions": "Ajustar clareza e CTA.",
                        "publication_permission": False,
                        "external_api_used": False,
                        "human_review_required": True,
                        "approved_for_auto_publish": False,
                    },
                    {
                        "task_id": "task_02",
                        "status": "pending_refinement",
                        "task_type": "ai_image_prompt",
                        "title": "Preparar prompt de imagem IA",
                        "product": "BRICS Paraguay Autos",
                        "objective": "validar campanha",
                        "approval_status": "needs_revision",
                        "review_notes": "Ajustar linguagem.",
                        "channels": ["Instagram"],
                        "instructions": "Criar prompt visual seguro.",
                        "publication_permission": False,
                        "external_api_used": False,
                        "human_review_required": True,
                        "approved_for_auto_publish": False,
                    },
                ],
            }

            queue_file.write_text(
                json.dumps(queue, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            executor = SocialContentRefinementExecutor(
                queue_file=queue_file,
                output_dir=output_dir,
            )

            summary = executor.execute()

            self.assertEqual(summary["tasks_found"], 2)
            self.assertEqual(summary["files_generated"], 2)
            self.assertFalse(summary["publication_permission"])
            self.assertFalse(summary["external_api_used"])
            self.assertTrue(summary["human_review_required"])
            self.assertFalse(summary["approved_for_auto_publish"])

            generated_files = list(output_dir.glob("*.md"))
            self.assertEqual(len(generated_files), 2)

            content = generated_files[0].read_text(encoding="utf-8")
            self.assertIn("Human review required: True", content)
            self.assertIn("Publication permission: False", content)

            self.assertTrue((output_dir / "refinement_execution_summary.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
