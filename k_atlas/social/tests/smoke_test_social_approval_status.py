# -*- coding: utf-8 -*-
"""Smoke test for K-Social approval status propagation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.analytics.social_cockpit_adapter import SocialCockpitAdapter
from k_atlas.social.reports.social_autoreporter import SocialAutoReporter


class TestSocialApprovalStatusPropagation(unittest.TestCase):
    """Validates approval status in snapshot and daily report."""

    def test_approval_status_reaches_snapshot_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir)
            output_file = reports_dir / "social_dashboard_snapshot.json"

            operation = {
                "system": "K-Social Intelligence System",
                "operation_status": "draft_ready_for_human_review",
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "audience": {
                    "product": "BRICS Paraguay Autos",
                    "market": "marketplace automotivo Paraguai-Brasil",
                    "segments": [
                        {"persona": "compradores brasileiros interessados em carros no Paraguai"}
                    ],
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
                        {"day": 1, "channel": "WhatsApp", "publish_automatically": False},
                    ],
                },
                "audit": {
                    "audit_status": "approved_for_human_review",
                    "errors": [],
                    "warnings": [],
                    "human_review_required": True,
                    "publication_permission": False,
                    "approved_for_auto_publish": False,
                },
                "request_metadata": {
                    "approval_status": "needs_revision",
                },
            }

            operation_path = reports_dir / "operation_test.json"
            operation_path.write_text(
                json.dumps(operation, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            adapter = SocialCockpitAdapter(
                reports_dir=reports_dir,
                output_file=output_file,
            )
            snapshot = adapter.save_snapshot()

            self.assertEqual(snapshot["total_operations"], 1)
            self.assertEqual(snapshot["approval_counts"]["needs_revision"], 1)
            self.assertEqual(snapshot["approval_counts"]["pending_human_review"], 0)
            self.assertEqual(snapshot["operations"][0]["approval_status"], "needs_revision")
            self.assertFalse(snapshot["approved_for_auto_publish"])

            reporter = SocialAutoReporter(
                snapshot_path=output_file,
                reports_dir=reports_dir,
            )
            report = reporter.run()

            self.assertEqual(report["summary"]["approval_counts"]["needs_revision"], 1)
            self.assertEqual(report["operations"][0]["approval_status"], "needs_revision")
            self.assertFalse(report["summary"]["approved_for_auto_publish"])

            markdown = (reports_dir / "social_daily_report.md").read_text(
                encoding="utf-8"
            )

            self.assertIn("Needs revision: 1", markdown)
            self.assertIn("Approval status: needs_revision", markdown)
            self.assertIn("Auto-publishing is blocked", markdown)


if __name__ == "__main__":
    unittest.main(verbosity=2)
