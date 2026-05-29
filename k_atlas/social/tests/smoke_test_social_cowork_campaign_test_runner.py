# -*- coding: utf-8 -*-
"""Smoke tests for K-Social Cowork campaign test runner."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.cowork.social_cowork_campaign_test_runner import (
    SocialCoworkCampaignTestRunner,
)


def build_approved_package() -> dict:
    return {
        "system": "K-Social Campaign Package Exporter",
        "package_name": "Parada Atlantida + Chopp Ecobier - Campanha Futebol 2026",
        "product_filter": "Parada Atlantida + Chopp Ecobier",
        "owner": "K-Atlas Operator",
        "generated_at": "2026-05-29T12:00:00+00:00",
        "total_assets": 2,
        "assets": [
            {
                "file_name": "parada-atlantida-chopp-ecobier_caption-refinement.md",
                "path": "local",
                "content": "# Caption\n\nProduct: Parada Atlantida + Chopp Ecobier\nPublication permission: False",
            },
            {
                "file_name": "parada-atlantida-chopp-ecobier_reel-script.md",
                "path": "local",
                "content": "# Reel\n\nApproved for auto publish: False",
            },
        ],
        "package_metadata": {
            "final_approval_status": "approved_for_manual_use",
            "last_reviewed_at": "2026-05-29T13:00:00+00:00",
        },
        "governance": {
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "requires_final_approval": True,
            "manual_use_only": True,
        },
    }


class TestSocialCoworkCampaignTestRunner(unittest.TestCase):
    """Validates full local Cowork dry-run flow."""

    def test_cowork_runner_generates_report_without_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            social_dir = Path(temp_dir)
            packages_dir = social_dir / "reports" / "campaign_packages"
            packages_dir.mkdir(parents=True, exist_ok=True)

            package_path = packages_dir / "ecobier_package.json"
            package_path.write_text(
                json.dumps(build_approved_package(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            runner = SocialCoworkCampaignTestRunner(social_dir=social_dir)
            result = runner.run(product_filter="Parada Atlantida + Chopp Ecobier")

            self.assertIn("Parada Atlantida", result["latest_campaign"]["package_name"])
            self.assertEqual(result["publish_result"]["payloads_planned"], 2)
            self.assertEqual(result["publish_result"]["payloads_validated"], 2)
            self.assertFalse(result["publication_permission"])
            self.assertFalse(result["external_api_used"])
            self.assertFalse(result["approved_for_auto_publish"])
            self.assertTrue(result["dry_run"])

            self.assertTrue(
                (social_dir / "reports" / "supervisor_reports" / "k_social_supervisor_report_ecobier_campaign.md").exists()
            )
            self.assertTrue(
                (social_dir / "reports" / "test_page_publish_receipts" / "latest_test_page_receipts.json").exists()
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
