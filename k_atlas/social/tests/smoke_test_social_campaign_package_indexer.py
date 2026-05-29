# -*- coding: utf-8 -*-
"""Smoke tests for K-Social campaign package indexer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.campaign_factory.social_campaign_package_indexer import (
    SocialCampaignPackageIndexer,
)


class TestSocialCampaignPackageIndexer(unittest.TestCase):
    """Validates clean campaign package index generation."""

    def test_indexer_builds_clean_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packages_dir = Path(temp_dir)

            valid_package = {
                "system": "K-Social Campaign Package Exporter",
                "package_name": "Valid Package",
                "owner": "K-Atlas Operator",
                "generated_at": "2026-05-29T10:00:00+00:00",
                "total_assets": 5,
                "governance": {
                    "human_review_required": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "requires_final_approval": True,
                },
            }

            invalid_package = {
                "system": "Other System",
                "package_name": "Invalid Package",
            }

            (packages_dir / "valid_package.json").write_text(
                json.dumps(valid_package, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (packages_dir / "valid_package.md").write_text(
                "# Valid Package",
                encoding="utf-8",
            )
            (packages_dir / "invalid_package.json").write_text(
                json.dumps(invalid_package, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            indexer = SocialCampaignPackageIndexer(packages_dir=packages_dir)
            index = indexer.save_index()

            self.assertEqual(index["system"], "K-Social Campaign Package Index")
            self.assertEqual(index["total_packages"], 1)
            self.assertEqual(index["latest_package"]["package_name"], "Valid Package")
            self.assertEqual(len(index["recent_packages"]), 1)
            self.assertFalse(index["governance"]["publication_permission"])
            self.assertFalse(index["governance"]["external_api_used"])
            self.assertFalse(index["governance"]["approved_for_auto_publish"])
            self.assertTrue(index["governance"]["human_review_required"])
            self.assertTrue((packages_dir / "campaign_package_index.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
