# -*- coding: utf-8 -*-
"""Smoke tests for K-Social Command Center."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.analytics.social_command_center import SocialCommandCenter


class TestSocialCommandCenter(unittest.TestCase):
    """Validates command center aggregation."""

    def test_command_center_builds_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            social_dir = Path(temp_dir)
            reports_dir = social_dir / "reports"
            memory_dir = social_dir / "memory"
            packages_dir = reports_dir / "campaign_packages"
            reports_dir.mkdir(parents=True, exist_ok=True)
            memory_dir.mkdir(parents=True, exist_ok=True)
            packages_dir.mkdir(parents=True, exist_ok=True)

            (reports_dir / "social_dashboard_snapshot.json").write_text(
                json.dumps(
                    {
                        "total_operations": 2,
                        "ready_for_review": 2,
                        "blocked_operations": 0,
                        "total_content_items": 30,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            (memory_dir / "social_approval_queue.json").write_text(
                json.dumps(
                    {
                        "total_items": 2,
                        "counts": {
                            "pending_human_review": 1,
                            "approved_for_content_refinement": 0,
                            "needs_revision": 1,
                            "rejected": 0,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            (memory_dir / "social_content_refinement_queue.json").write_text(
                json.dumps(
                    {
                        "total_tasks": 5,
                        "counts": {
                            "pending_refinement": 5,
                            "in_progress": 0,
                            "done": 0,
                            "blocked": 0,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            (packages_dir / "campaign_package_index.json").write_text(
                json.dumps(
                    {
                        "total_packages": 3,
                        "recent_packages": [{"package_name": "Recent"}],
                        "latest_package": {"package_name": "Latest"},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            (memory_dir / "campaign_package_approval_queue.json").write_text(
                json.dumps(
                    {
                        "total_items": 3,
                        "counts": {
                            "pending_final_review": 2,
                            "approved_for_manual_use": 1,
                            "needs_package_revision": 0,
                            "rejected": 0,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            command_center = SocialCommandCenter(social_dir=social_dir)
            data = command_center.save()

            self.assertEqual(data["operations"]["total"], 2)
            self.assertEqual(data["approval_queue"]["needs_revision"], 1)
            self.assertEqual(data["refinement_queue"]["total_tasks"], 5)
            self.assertEqual(data["campaign_packages"]["total"], 3)
            self.assertEqual(data["package_approval"]["approved_for_manual_use"], 1)
            self.assertFalse(data["governance"]["approved_for_auto_publish"])
            self.assertTrue((reports_dir / "social_command_center.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
