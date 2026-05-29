# -*- coding: utf-8 -*-
"""Smoke tests for K-Social campaign package viewer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.ui.social_campaign_packages_view import load_campaign_package_index


class TestSocialCampaignPackageViewer(unittest.TestCase):
    """Validates loading campaign package index for cockpit."""

    def test_load_campaign_package_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packages_dir = Path(temp_dir)

            index = {
                "system": "K-Social Campaign Package Index",
                "total_packages": 1,
                "latest_package": {
                    "package_name": "Test Package",
                    "total_assets": 5,
                },
                "recent_packages": [],
                "all_packages": [],
                "governance": {
                    "human_review_required": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "requires_final_approval": True,
                },
            }

            (packages_dir / "campaign_package_index.json").write_text(
                json.dumps(index, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            data = load_campaign_package_index(packages_dir=packages_dir)

            self.assertTrue(data["index_found"])
            self.assertEqual(data["total_packages"], 1)
            self.assertEqual(data["latest_package"]["package_name"], "Test Package")
            self.assertFalse(data["governance"]["publication_permission"])
            self.assertFalse(data["governance"]["external_api_used"])
            self.assertFalse(data["governance"]["approved_for_auto_publish"])
            self.assertTrue(data["governance"]["human_review_required"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
