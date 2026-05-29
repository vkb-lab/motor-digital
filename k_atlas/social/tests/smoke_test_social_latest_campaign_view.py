# -*- coding: utf-8 -*-
"""Smoke tests for latest campaign cockpit view."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.ui.social_latest_campaign_view import (
    load_latest_manual_approved_campaign,
)


class TestSocialLatestCampaignView(unittest.TestCase):
    """Validates latest campaign loading."""

    def test_load_latest_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            latest_path = Path(temp_dir) / "latest_manual_approved_campaign.json"

            payload = {
                "system": "K-Social Latest Manual Approved Campaign",
                "latest_found": True,
                "campaign": {
                    "package_name": "Parada Atlantida + Chopp Ecobier",
                    "approval_status": "approved_for_manual_use",
                    "total_assets": 5,
                },
                "governance": {
                    "human_review_required": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "manual_use_only": True,
                },
            }

            latest_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            data = load_latest_manual_approved_campaign(latest_path=latest_path)

            self.assertTrue(data["latest_found"])
            self.assertEqual(
                data["campaign"]["approval_status"],
                "approved_for_manual_use",
            )
            self.assertFalse(data["governance"]["publication_permission"])
            self.assertFalse(data["governance"]["approved_for_auto_publish"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
