# -*- coding: utf-8 -*-
"""Smoke tests for K-Social campaign package exporter."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.campaign_factory.social_campaign_package_exporter import (
    SocialCampaignPackageExporter,
)


class TestSocialCampaignPackageExporter(unittest.TestCase):
    """Validates local campaign package export."""

    def test_exporter_builds_json_and_markdown_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            refinement_dir = base_dir / "refinement_outputs"
            output_dir = base_dir / "campaign_packages"
            refinement_dir.mkdir(parents=True, exist_ok=True)

            (refinement_dir / "caption_refinement.md").write_text(
                "# Caption\n\nHuman review required: True\nPublication permission: False",
                encoding="utf-8",
            )
            (refinement_dir / "reel_script.md").write_text(
                "# Reel Script\n\nApproved for auto publish: False",
                encoding="utf-8",
            )

            exporter = SocialCampaignPackageExporter(
                refinement_outputs_dir=refinement_dir,
                output_dir=output_dir,
            )

            result = exporter.run(
                package_name="Test Campaign Package",
                owner="K-Atlas Operator",
            )

            package = result["package"]

            self.assertEqual(package["total_assets"], 2)
            self.assertFalse(result["publication_permission"])
            self.assertFalse(result["external_api_used"])
            self.assertTrue(result["human_review_required"])
            self.assertFalse(result["approved_for_auto_publish"])
            self.assertFalse(package["governance"]["publication_permission"])
            self.assertTrue(package["governance"]["requires_final_approval"])

            json_path = Path(result["paths"]["json_path"])
            md_path = Path(result["paths"]["markdown_path"])

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

            loaded_package = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertEqual(loaded_package["total_assets"], 2)

            md_content = md_path.read_text(encoding="utf-8")

            self.assertIn("K-Social Campaign Package", md_content)
            self.assertIn("Human review required", md_content)
            self.assertIn("Approved for auto publish: False", md_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
