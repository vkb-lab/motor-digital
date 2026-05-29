from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.official_channels.instagram.export_plan import export_instagram_plan
from k_atlas.social.official_channels.instagram.governance import validate_instagram_official_payload
from k_atlas.social.official_channels.instagram.identity import build_k_atlas_instagram_identity
from k_atlas.social.official_channels.instagram.strategy import build_instagram_launch_strategy


class InstagramOfficialSmokeTest(unittest.TestCase):
    def test_identity_exists(self) -> None:
        identity = build_k_atlas_instagram_identity()
        self.assertEqual(identity.display_name, "K-Atlas OS")
        self.assertGreaterEqual(len(identity.content_pillars), 5)

    def test_strategy_is_planning_only(self) -> None:
        strategy = build_instagram_launch_strategy()
        self.assertEqual(strategy["status"], "planning_only")
        self.assertFalse(strategy["official_publish_allowed"])
        self.assertFalse(strategy["auto_publish_allowed"])

    def test_governance_blocks_official_publish(self) -> None:
        result = validate_instagram_official_payload({
            "official_publish": True,
            "auto_publish": False,
        })
        self.assertFalse(result["ok"])
        self.assertIn("official_publish_blocked_until_level_4", result["reasons"])

    def test_export_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "plan.json"
            report = export_instagram_plan(str(output))
            self.assertTrue(output.exists())
            self.assertTrue(report["ok"])

            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(loaded["checkpoint"], "31")


if __name__ == "__main__":
    unittest.main(verbosity=2)