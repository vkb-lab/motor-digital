# -*- coding: utf-8 -*-
"""Smoke test for K-Social report isolation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.analytics.social_cockpit_adapter import SocialCockpitAdapter


class TestSocialReportIsolation(unittest.TestCase):
    """Ensures daily reports are not counted as social operations."""

    def test_adapter_ignores_daily_report_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir)
            output_file = reports_dir / "social_dashboard_snapshot.json"

            valid_operation = {
                "system": "K-Social Intelligence System",
                "operation_status": "draft_ready_for_human_review",
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "audience": {
                    "product": "BRICS Paraguay Autos",
                    "market": "marketplace automotivo Paraguai-Brasil",
                },
                "creative_brief": {
                    "product": "BRICS Paraguay Autos",
                    "objective": "validar campanha supervisionada",
                },
                "campaign": {
                    "objective": "validar campanha supervisionada",
                    "channels": ["Instagram", "Facebook", "WhatsApp"],
                    "duration_days": 5,
                    "content_calendar": [
                        {"day": 1, "channel": "Instagram", "publish_automatically": False},
                        {"day": 1, "channel": "Facebook", "publish_automatically": False},
                    ],
                },
                "audit": {
                    "audit_status": "approved_for_human_review",
                },
            }

            daily_report = {
                "system": "K-Social AutoReporter",
                "summary": {
                    "total_operations": 99,
                    "ready_for_review": 99,
                    "blocked_operations": 99,
                    "total_content_items": 99,
                },
                "operations": [],
            }

            invalid_json_like_report = {
                "system": "Random Report",
                "summary": {},
            }

            (reports_dir / "valid_operation.json").write_text(
                json.dumps(valid_operation, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            (reports_dir / "social_daily_report.json").write_text(
                json.dumps(daily_report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            (reports_dir / "random_report.json").write_text(
                json.dumps(invalid_json_like_report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            adapter = SocialCockpitAdapter(
                reports_dir=reports_dir,
                output_file=output_file,
            )

            snapshot = adapter.save_snapshot()

            self.assertTrue(output_file.exists())
            self.assertEqual(snapshot["total_operations"], 1)
            self.assertEqual(snapshot["ready_for_review"], 1)
            self.assertEqual(snapshot["blocked_operations"], 0)
            self.assertEqual(snapshot["total_content_items"], 2)
            self.assertEqual(snapshot["operations"][0]["source_file"], "valid_operation.json")
            self.assertEqual(snapshot["operations"][0]["product"], "BRICS Paraguay Autos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
