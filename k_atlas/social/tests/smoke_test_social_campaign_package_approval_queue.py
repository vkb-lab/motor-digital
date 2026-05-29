# -*- coding: utf-8 -*-
"""Smoke tests for K-Social package approval queue."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.audit.social_campaign_package_approval_queue import (
    SocialCampaignPackageApprovalQueue,
)


def build_valid_package() -> dict:
    return {
        "system": "K-Social Campaign Package Exporter",
        "package_name": "Test Campaign Package",
        "owner": "K-Atlas Operator",
        "generated_at": "2026-05-29T10:00:00+00:00",
        "total_assets": 5,
        "governance": {
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "requires_final_approval": True,
        },
    }


class TestSocialCampaignPackageApprovalQueue(unittest.TestCase):
    """Validates final package approval queue."""

    def test_package_approval_queue_updates_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            packages_dir = base_dir / "campaign_packages"
            memory_dir = base_dir / "memory"
            packages_dir.mkdir(parents=True, exist_ok=True)
            memory_dir.mkdir(parents=True, exist_ok=True)

            package_path = packages_dir / "package_test.json"
            package_path.write_text(
                json.dumps(build_valid_package(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            queue_manager = SocialCampaignPackageApprovalQueue(
                packages_dir=packages_dir,
                memory_dir=memory_dir,
            )

            queue = queue_manager.save_queue()

            self.assertEqual(queue["total_items"], 1)
            self.assertEqual(queue["counts"]["pending_final_review"], 1)
            self.assertFalse(queue["publication_permission"])
            self.assertFalse(queue["approved_for_auto_publish"])

            updated_queue = queue_manager.update_decision(
                source_file="package_test.json",
                decision="approved_for_manual_use",
                reviewer="K-Atlas Operator",
                notes="Liberado apenas para uso manual.",
            )

            self.assertEqual(updated_queue["counts"]["approved_for_manual_use"], 1)
            self.assertEqual(updated_queue["counts"]["pending_final_review"], 0)

            package = json.loads(package_path.read_text(encoding="utf-8"))

            self.assertEqual(
                package["package_metadata"]["final_approval_status"],
                "approved_for_manual_use",
            )
            self.assertFalse(package["governance"]["publication_permission"])
            self.assertFalse(package["governance"]["approved_for_auto_publish"])
            self.assertEqual(len(package["final_approval_events"]), 1)

    def test_package_approval_rejects_auto_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue_manager = SocialCampaignPackageApprovalQueue(
                packages_dir=Path(temp_dir) / "campaign_packages",
                memory_dir=Path(temp_dir) / "memory",
            )

            with self.assertRaises(ValueError):
                queue_manager.update_decision(
                    source_file="missing.json",
                    decision="approved_for_auto_publish",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
