# -*- coding: utf-8 -*-
"""Smoke tests for K-Social Intelligence System."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.social_orchestrator import SocialOrchestrator


class TestKSocialSystem(unittest.TestCase):
    """Validates the first supervised K-Social kernel."""

    def test_full_social_operation_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = SocialOrchestrator(memory_dir=Path(temp_dir))

            result = orchestrator.plan_social_operation(
                product="Closet Pilot",
                market="moda e organizacao pessoal",
                personas=[
                    "mulheres ocupadas que querem montar looks mais rapido",
                    "consultoras de imagem que precisam organizar pecas",
                ],
                objective="validar interesse inicial com campanha supervisionada",
                channels=["Instagram", "TikTok", "Facebook"],
                duration_days=3,
                key_messages=[
                    "organize seu guarda-roupa com mais clareza",
                    "monte looks com menos friccao",
                    "teste uma experiencia simples antes de escalar",
                ],
                format_type="reel",
                brand_tone="premium, simples e util",
                region="Brasil",
                language="pt-BR",
                seasonal_context="campanha local inicial",
            )

            self.assertEqual(result["system"], "K-Social Intelligence System")
            self.assertFalse(result["publication_permission"])
            self.assertFalse(result["external_api_used"])
            self.assertTrue(result["human_review_required"])

            self.assertIn("audience", result)
            self.assertIn("creative_brief", result)
            self.assertIn("campaign", result)
            self.assertIn("audit", result)

            self.assertEqual(result["audit"]["audit_status"], "approved_for_human_review")
            self.assertFalse(result["audit"]["approved_for_auto_publish"])

            campaign = result["campaign"]
            self.assertEqual(campaign["duration_days"], 3)
            self.assertEqual(len(campaign["channels"]), 3)
            self.assertEqual(len(campaign["content_calendar"]), 9)

            for item in campaign["content_calendar"]:
                self.assertFalse(item["publish_automatically"])
                self.assertEqual(item["content_status"], "draft_needs_human_review")

            memory_file = Path(temp_dir) / "audience_memory.json"
            self.assertTrue(memory_file.exists())

            with memory_file.open("r", encoding="utf-8") as file:
                memory = json.load(file)

            self.assertIn("audiences", memory)
            self.assertEqual(len(memory["audiences"]), 1)

    def test_auditor_blocks_auto_publish(self) -> None:
        orchestrator = SocialOrchestrator()

        unsafe_campaign = {
            "duration_days": 1,
            "channels": ["Instagram"],
            "content_calendar": [
                {
                    "caption_draft": "Teste de campanha.",
                    "publish_automatically": True,
                }
            ],
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
        }

        audit = orchestrator.audit_campaign(unsafe_campaign)

        self.assertEqual(audit["audit_status"], "blocked")
        self.assertFalse(audit["publication_permission"])
        self.assertFalse(audit["approved_for_auto_publish"])
        self.assertGreater(len(audit["errors"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
