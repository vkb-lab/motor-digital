# -*- coding: utf-8 -*-
"""Smoke tests for K-Social AutoReporter."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.reports.social_autoreporter import SocialAutoReporter


class TestSocialAutoReporter(unittest.TestCase):
    """Validates daily report generation."""

    def test_autoreporter_generates_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir)
            snapshot_path = reports_dir / "social_dashboard_snapshot.json"

            snapshot = {
                "system": "K-Social Cockpit Snapshot",
                "total_operations": 1,
                "ready_for_review": 1,
                "blocked_operations": 0,
                "total_content_items": 15,
                "publication_permission": False,
                "external_api_used": False,
                "human_review_required": True,
                "operations": [
                    {
                        "product": "BRICS Paraguay Autos",
                        "market": "marketplace automotivo Paraguai-Brasil",
                        "objective": "validar campanha local supervisionada",
                        "audit_status": "approved_for_human_review",
                        "channels": ["Instagram", "Facebook", "WhatsApp"],
                        "content_items": 15,
                        "human_review_required": True,
                        "publication_permission": False,
                    }
                ],
            }

            with snapshot_path.open("w", encoding="utf-8") as file:
                json.dump(snapshot, file, ensure_ascii=False, indent=2)

            reporter = SocialAutoReporter(
                snapshot_path=snapshot_path,
                reports_dir=reports_dir,
            )

            report = reporter.run()

            self.assertEqual(report["system"], "K-Social AutoReporter")
            self.assertEqual(report["summary"]["total_operations"], 1)
            self.assertEqual(report["summary"]["ready_for_review"], 1)
            self.assertEqual(report["summary"]["blocked_operations"], 0)
            self.assertEqual(report["summary"]["total_content_items"], 15)
            self.assertFalse(report["summary"]["publication_permission"])
            self.assertFalse(report["summary"]["external_api_used"])
            self.assertTrue(report["summary"]["human_review_required"])

            self.assertTrue((reports_dir / "social_daily_report.json").exists())
            self.assertTrue((reports_dir / "social_daily_report.md").exists())

            md_content = (reports_dir / "social_daily_report.md").read_text(
                encoding="utf-8"
            )

            self.assertIn("K-Social Daily Report", md_content)
            self.assertIn("BRICS Paraguay Autos", md_content)
            self.assertIn("Auto-publishing is blocked", md_content)

    def test_autoreporter_handles_missing_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir)
            missing_snapshot = reports_dir / "missing_snapshot.json"

            reporter = SocialAutoReporter(
                snapshot_path=missing_snapshot,
                reports_dir=reports_dir,
            )

            report = reporter.run()

            self.assertFalse(report["snapshot_found"])
            self.assertEqual(report["summary"]["total_operations"], 0)
            self.assertFalse(report["summary"]["publication_permission"])
            self.assertFalse(report["summary"]["external_api_used"])
            self.assertTrue(report["summary"]["human_review_required"])
            self.assertTrue((reports_dir / "social_daily_report.json").exists())
            self.assertTrue((reports_dir / "social_daily_report.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
