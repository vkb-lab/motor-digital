# -*- coding: utf-8 -*-
"""Smoke tests for K-Social campaign package cleanup."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.campaign_factory.social_campaign_package_cleanup import (
    SocialCampaignPackageCleanup,
)


def build_package(name: str, status: str, reviewed_at: str) -> dict:
    return {
        "system": "K-Social Campaign Package Exporter",
        "package_name": name,
        "product_filter": "Parada Atlantida + Chopp Ecobier",
        "owner": "K-Atlas Operator",
        "generated_at": reviewed_at,
        "total_assets": 5,
        "package_metadata": {
            "final_approval_status": status,
            "last_reviewed_at": reviewed_at,
        },
        "governance": {
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "requires_final_approval": True,
        },
    }


class TestSocialCampaignPackageCleanup(unittest.TestCase):
    """Validates latest manually approved package selection."""

    def test_cleanup_selects_latest_manual_approved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packages_dir = Path(temp_dir)

            older = build_package(
                "Older Ecobier Package",
                "approved_for_manual_use",
                "2026-05-29T10:00:00+00:00",
            )
            latest = build_package(
                "Latest Ecobier Package",
                "approved_for_manual_use",
                "2026-05-29T12:00:00+00:00",
            )
            pending = build_package(
                "Pending Ecobier Package",
                "pending_final_review",
                "2026-05-29T13:00:00+00:00",
            )

            (packages_dir / "older.json").write_text(
                json.dumps(older, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (packages_dir / "latest.json").write_text(
                json.dumps(latest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (packages_dir / "pending.json").write_text(
                json.dumps(pending, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            cleanup = SocialCampaignPackageCleanup(packages_dir=packages_dir)
            index = cleanup.run(product_filter="Parada Atlantida + Chopp Ecobier")

            self.assertEqual(index["total_valid_packages"], 3)
            self.assertEqual(index["total_manual_approved"], 2)
            self.assertEqual(
                index["latest_manual_approved"]["package_name"],
                "Latest Ecobier Package",
            )
            self.assertEqual(len(index["archived_manual_approved"]), 1)
            self.assertFalse(index["governance"]["approved_for_auto_publish"])
            self.assertTrue((packages_dir / "latest_manual_approved_campaign.json").exists())
            self.assertTrue((packages_dir / "latest_manual_approved_campaign.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
