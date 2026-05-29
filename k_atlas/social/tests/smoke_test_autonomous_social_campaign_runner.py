# -*- coding: utf-8 -*-
"""Smoke tests for autonomous social campaign runner."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from k_atlas.social.campaign_factory.autonomous_social_campaign_runner import (
    AutonomousSocialCampaignRunner,
)


class TestAutonomousSocialCampaignRunner(unittest.TestCase):
    """Validates autonomous supervised campaign generation."""

    def test_runner_creates_supervised_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            social_dir = Path(temp_dir)
            runner = AutonomousSocialCampaignRunner(social_dir=social_dir)

            result = runner.run()

            self.assertEqual(result["system"], "K-Social Autonomous Campaign Runner")
            self.assertIn("Parada Atlantida", result["campaign"])
            self.assertIn("Chopp Ecobier", result["campaign"])
            self.assertTrue(result["human_review_required"])
            self.assertFalse(result["publication_permission"])
            self.assertFalse(result["external_api_used"])
            self.assertFalse(result["approved_for_auto_publish"])
            self.assertTrue(Path(result["request_file"]).exists())
            self.assertTrue(Path(result["operation_file"]).exists())
            self.assertGreaterEqual(result["snapshot_total_operations"], 1)
            self.assertGreaterEqual(result["approval_queue_total"], 1)
            self.assertGreaterEqual(result["command_center_operations"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
