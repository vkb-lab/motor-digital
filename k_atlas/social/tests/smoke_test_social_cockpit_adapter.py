# -*- coding: utf-8 -*-
"""Smoke test for K-Social cockpit adapter."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.analytics.social_cockpit_adapter import SocialCockpitAdapter


class TestSocialCockpitAdapter(unittest.TestCase):
    """Validates dashboard snapshot generation."""

    def test_build_dashboard_snapshot_from_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir)
            output_file = reports_dir / "social_dashboard_snapshot.json"

            sample_report = {
                "operation_status": "draft_ready_for_human_review",
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "audience": {
                    "product": "BRICS Paraguay Autos",
                    "market": "marketplace automotivo Paraguai-Brasil",
                },
                "creative_brief": {
                    "objective": "validar campanha supervisionada",
                },
                "campaign": {
                    "objective": "validar campanha supervisionada",
                    "channels": ["Instagram", "Facebook", "WhatsApp"],
                    "duration_days": 5,
                    "content_calendar": [
                        {"day": 1, "channel": "Instagram", "publish_automatically": False},
                        {"day": 1, "channel": "Facebook", "publish_automatically": False},
                        {"day": 1, "channel": "WhatsApp", "publish_automatically": False},
                    ],
                },
                "audit": {
                    "audit_status": "approved_for_human_review",
                },
            }

            report_file = reports_dir / "social_demo_operation.json"
            with report_file.open("w", encoding="utf-8") as file:
                json.dump(sample_report, file, ensure_ascii=False, indent=2)

            adapter = SocialCockpitAdapter(
                reports_dir=reports_dir,
                output_file=output_file,
            )

            snapshot = adapter.save_snapshot()

            self.assertTrue(output_file.exists())
            self.assertEqual(snapshot["system"], "K-Social Cockpit Snapshot")
            self.assertEqual(snapshot["total_operations"], 1)
            self.assertEqual(snapshot["ready_for_review"], 1)
            self.assertEqual(snapshot["blocked_operations"], 0)
            self.assertEqual(snapshot["total_content_items"], 3)
            self.assertFalse(snapshot["publication_permission"])
            self.assertFalse(snapshot["external_api_used"])
            self.assertTrue(snapshot["human_review_required"])
            self.assertEqual(snapshot["operations"][0]["product"], "BRICS Paraguay Autos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
