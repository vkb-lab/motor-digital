# -*- coding: utf-8 -*-
"""Smoke tests for K-Social refinement outputs viewer."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from k_atlas.social.ui.social_refinement_outputs_view import load_refinement_outputs


class TestSocialRefinementOutputsViewer(unittest.TestCase):
    """Validates loading generated refinement outputs."""

    def test_load_refinement_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs_dir = Path(temp_dir)

            file_a = outputs_dir / "caption_refinement.md"
            file_b = outputs_dir / "ai_image_prompt.md"

            file_a.write_text(
                "# Caption Refinement\n\nHuman review required: True\nPublication permission: False",
                encoding="utf-8",
            )
            file_b.write_text(
                "# AI Image Prompt\n\nApproved for auto publish: False",
                encoding="utf-8",
            )

            data = load_refinement_outputs(outputs_dir=outputs_dir)

            self.assertEqual(data["system"], "K-Social Refinement Outputs Viewer")
            self.assertEqual(data["total_files"], 2)
            self.assertFalse(data["publication_permission"])
            self.assertFalse(data["external_api_used"])
            self.assertTrue(data["human_review_required"])
            self.assertFalse(data["approved_for_auto_publish"])

            names = [item["file_name"] for item in data["files"]]

            self.assertIn("caption_refinement.md", names)
            self.assertIn("ai_image_prompt.md", names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
