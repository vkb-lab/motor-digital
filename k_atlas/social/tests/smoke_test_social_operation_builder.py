# -*- coding: utf-8 -*-
"""Smoke tests for K-Social Operation Builder."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.campaign_factory.social_operation_builder import SocialOperationBuilder


class TestSocialOperationBuilder(unittest.TestCase):
    """Validates supervised operation creation from JSON requests."""

    def test_builder_creates_operation_and_refreshes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            requests_dir = base_dir / "memory"
            reports_dir = base_dir / "reports"
            requests_dir.mkdir(parents=True, exist_ok=True)
            reports_dir.mkdir(parents=True, exist_ok=True)

            request_path = requests_dir / "request.json"

            request = {
                "request_name": "closet_pilot_test",
                "owner": "K-Atlas Operator",
                "product": "Closet Pilot",
                "market": "moda e organizacao pessoal",
                "personas": [
                    "mulheres ocupadas que querem montar looks mais rapido"
                ],
                "objective": "validar interesse inicial",
                "channels": ["Instagram", "TikTok"],
                "duration_days": 2,
                "key_messages": [
                    "monte looks com menos friccao",
                    "organize seu guarda-roupa com clareza"
                ],
                "format_type": "reel",
                "brand_tone": "premium, simples e util",
                "region": "Brasil",
                "language": "pt-BR",
                "seasonal_context": "campanha local inicial"
            }

            request_path.write_text(
                json.dumps(request, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            builder = SocialOperationBuilder(
                requests_dir=requests_dir,
                reports_dir=reports_dir,
            )

            result = builder.run_from_request_file(request_path)

            self.assertEqual(result["status"], "operation_created")
            self.assertFalse(result["publication_permission"])
            self.assertFalse(result["external_api_used"])
            self.assertTrue(result["human_review_required"])
            self.assertEqual(result["snapshot_total_operations"], 1)
            self.assertEqual(result["daily_report_total_operations"], 1)

            operation_file = Path(result["operation_file"])
            self.assertTrue(operation_file.exists())
            self.assertTrue((reports_dir / "social_dashboard_snapshot.json").exists())
            self.assertTrue((reports_dir / "social_daily_report.json").exists())
            self.assertTrue((reports_dir / "social_daily_report.md").exists())

            operation = json.loads(operation_file.read_text(encoding="utf-8"))

            self.assertEqual(operation["audience"]["product"], "Closet Pilot")
            self.assertEqual(operation["audit"]["audit_status"], "approved_for_human_review")
            self.assertFalse(operation["publication_permission"])
            self.assertTrue(operation["human_review_required"])

    def test_builder_rejects_invalid_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            requests_dir = base_dir / "memory"
            reports_dir = base_dir / "reports"
            requests_dir.mkdir(parents=True, exist_ok=True)
            reports_dir.mkdir(parents=True, exist_ok=True)

            request_path = requests_dir / "invalid_request.json"
            request_path.write_text(
                json.dumps({"product": "Invalid"}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            builder = SocialOperationBuilder(
                requests_dir=requests_dir,
                reports_dir=reports_dir,
            )

            with self.assertRaises(ValueError):
                builder.run_from_request_file(request_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
