# -*- coding: utf-8 -*-
"""Smoke tests for K-Social product campaign package exporter."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.campaign_factory.social_product_campaign_package_exporter import (
    SocialProductCampaignPackageExporter,
)


class TestSocialProductCampaignPackageExporter(unittest.TestCase):
    """Validates product-specific package export."""

    def test_exports_only_matching_product_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            refinement_dir = base_dir / "refinement_outputs"
            output_dir = base_dir / "campaign_packages"
            refinement_dir.mkdir(parents=True, exist_ok=True)

            (refinement_dir / "parada-atlantida-chopp-ecobier_caption-refinement.md").write_text(
                "# Caption\n\nProduct: Parada Atlantida + Chopp Ecobier\nPublication permission: False",
                encoding="utf-8",
            )

            (refinement_dir / "brics-paraguay-autos_caption-refinement.md").write_text(
                "# Caption\n\nProduct: BRICS Paraguay Autos",
                encoding="utf-8",
            )

            exporter = SocialProductCampaignPackageExporter(
                refinement_outputs_dir=refinement_dir,
                output_dir=output_dir,
            )

            result = exporter.run(
                package_name="Parada Atlantida + Chopp Ecobier Campaign Package",
                product_filter="Parada Atlantida + Chopp Ecobier",
            )

            package = result["package"]

            self.assertEqual(package["total_assets"], 1)
            self.assertIn("Parada Atlantida", package["assets"][0]["content"])
            self.assertFalse(result["publication_permission"])
            self.assertFalse(result["approved_for_auto_publish"])
            self.assertTrue(result["human_review_required"])

            json_path = Path(result["paths"]["json_path"])
            md_path = Path(result["paths"]["markdown_path"])

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

            loaded = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertEqual(loaded["total_assets"], 1)
            self.assertFalse(loaded["governance"]["publication_permission"])
            self.assertTrue(loaded["governance"]["manual_use_only"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
