# -*- coding: utf-8 -*-
"""Smoke tests for K-Social daily report cockpit viewer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.ui.social_cockpit_view import (
    build_social_report_summary,
    load_social_report,
)


class TestSocialDailyReportViewer(unittest.TestCase):
    """Validates report loading and summary generation."""

    def test_load_missing_report_returns_safe_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = load_social_report(
                report_json_path=Path(temp_dir) / "missing.json",
                report_md_path=Path(temp_dir) / "missing.md",
            )

            self.assertFalse(report["report_found"])
            self.assertFalse(report["json_found"])
            self.assertFalse(report["markdown_found"])

            summary = build_social_report_summary(report)

            self.assertFalse(summary["report_found"])
            self.assertEqual(summary["total_operations"], 0)
            self.assertEqual(summary["ready_for_review"], 0)
            self.assertEqual(summary["blocked_operations"], 0)
            self.assertEqual(summary["total_content_items"], 0)

    def test_load_existing_report_returns_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "social_daily_report.json"
            md_path = Path(temp_dir) / "social_daily_report.md"

            payload = {
                "system": "K-Social AutoReporter",
                "generated_at": "2026-05-29T00:00:00+00:00",
                "summary": {
                    "total_operations": 1,
                    "ready_for_review": 1,
                    "blocked_operations": 0,
                    "total_content_items": 15,
                    "human_review_required": True,
                    "publication_permission": False,
                    "external_api_used": False,
                },
                "risks": [],
                "next_actions": [
                    "Review approved-for-human-review social operations.",
                    "Keep auto-publishing disabled.",
                ],
                "operations": [],
            }

            json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            md_path.write_text("# K-Social Daily Report", encoding="utf-8")

            report = load_social_report(
                report_json_path=json_path,
                report_md_path=md_path,
            )
            summary = build_social_report_summary(report)

            self.assertTrue(summary["report_found"])
            self.assertTrue(report["json_found"])
            self.assertTrue(report["markdown_found"])
            self.assertEqual(summary["total_operations"], 1)
            self.assertEqual(summary["ready_for_review"], 1)
            self.assertEqual(summary["blocked_operations"], 0)
            self.assertEqual(summary["total_content_items"], 15)
            self.assertEqual(len(summary["next_actions"]), 2)
            self.assertIn("K-Social Daily Report", summary["markdown"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
