# -*- coding: utf-8 -*-
"""Smoke tests for K-Social campaign package viewer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.ui.social_campaign_packages_view import load_campaign_packages


class TestSocialCampaignPackageViewer(unittest.TestCase):
    """Validates loading campaign packages for cockpit."""

    def test_load_campaign_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packages_dir = Path(temp_dir)

            package_json = {
                "system": "K-Social Campaign Package Exporter",
                "package_name": "Test Campaign Package",
                "total_assets": 2,
                "governance": {
                    "human_review_required": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "requires_final_approval": True,
                },
            }

            (packages_dir / "package.json").write_text(
                json.dumps(package_json, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            (packages_dir / "package.md").write_text(
                "# K-Social Campaign Package\n\nPublication permission: False",
                encoding="utf-8",
            )

            data = load_campaign_packages(packages_dir=packages_dir)

            self.assertEqual(data["system"], "K-Social Campaign Package Viewer")
            self.assertEqual(data["total_json_packages"], 1)
            self.assertEqual(data["total_markdown_packages"], 1)
            self.assertFalse(data["publication_permission"])
            self.assertFalse(data["external_api_used"])
            self.assertTrue(data["human_review_required"])
            self.assertFalse(data["approved_for_auto_publish"])

            self.assertEqual(data["json_packages"][0]["package_name"], "Test Campaign Package")
            self.assertIn("Publication permission", data["markdown_packages"][0]["content"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
