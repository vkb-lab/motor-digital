# -*- coding: utf-8 -*-
"""Smoke tests for K-Social cockpit UI layer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.ui.social_cockpit_view import (
    build_social_cockpit_summary,
    load_social_snapshot,
)


class TestSocialCockpitView(unittest.TestCase):
    """Validates dashboard data preparation without requiring Streamlit."""

    def test_load_missing_snapshot_returns_safe_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing_snapshot.json"

            snapshot = load_social_snapshot(missing_path)

            self.assertFalse(snapshot["snapshot_found"])
            self.assertEqual(snapshot["total_operations"], 0)
            self.assertFalse(snapshot["publication_permission"])
            self.assertFalse(snapshot["external_api_used"])
            self.assertTrue(snapshot["human_review_required"])

    def test_build_summary_from_existing_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = Path(temp_dir) / "social_dashboard_snapshot.json"

            payload = {
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
                        "market": "marketplace automotivo",
                        "objective": "validar campanha",
                        "audit_status": "approved_for_human_review",
                    }
                ],
            }

            with snapshot_path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)

            snapshot = load_social_snapshot(snapshot_path)
            summary = build_social_cockpit_summary(snapshot)

            self.assertTrue(summary["snapshot_found"])
            self.assertEqual(summary["total_operations"], 1)
            self.assertEqual(summary["ready_for_review"], 1)
            self.assertEqual(summary["blocked_operations"], 0)
            self.assertEqual(summary["total_content_items"], 15)
            self.assertFalse(summary["publication_permission"])
            self.assertFalse(summary["external_api_used"])
            self.assertTrue(summary["human_review_required"])
            self.assertEqual(summary["operations"][0]["product"], "BRICS Paraguay Autos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
