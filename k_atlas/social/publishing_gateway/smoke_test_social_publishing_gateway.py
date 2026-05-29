from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.social.publishing_gateway.approval_policy import ApprovalStatus
from k_atlas.social.publishing_gateway.audit_log import AuditLog
from k_atlas.social.publishing_gateway.channel_registry import build_default_channel_registry
from k_atlas.social.publishing_gateway.dry_run_adapter import DryRunAdapter
from k_atlas.social.publishing_gateway.permission_model import PermissionDecision, evaluate_permission
from k_atlas.social.publishing_gateway.publish_queue import PublishQueue
from k_atlas.social.publishing_gateway.test_page_adapter import TestPageAdapter


class SocialPublishingGatewaySmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ksocial_gateway_"))
        self.audit_path = self.tmp / "audit.jsonl"
        self.queue_path = self.tmp / "queue.json"
        self.test_page_path = self.tmp / "test_page_posts.jsonl"
        self.audit = AuditLog(self.audit_path)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def base_payload(self) -> dict:
        return {
            "campaign_id": "parada-atlantida-ecobier-futebol-2026",
            "channel": "test_page",
            "autonomy_level": "level_2_sandbox_page",
            "content": {
                "title": "Parada Atlantida + Chopp Ecobier",
                "body": "Campanha de teste para validacao operacional no sandbox.",
                "cta": "Validar criativo",
            },
            "human_approval": {
                "approved": True,
                "reviewer": "k_atlas_engineer",
            },
            "external_api_used": False,
            "publish_real": False,
            "mass_messaging": False,
            "browser_automation": False,
        }

    def test_registry_contains_expected_channels(self) -> None:
        registry = build_default_channel_registry()
        channels = set(registry.to_dict().keys())

        self.assertIn("dry_run", channels)
        self.assertIn("test_page", channels)
        self.assertIn("instagram_sandbox", channels)
        self.assertIn("whatsapp_sandbox", channels)
        self.assertIn("email_sandbox", channels)
        self.assertIn("instagram_official", channels)

    def test_dry_run_is_realistic_and_has_no_external_side_effect(self) -> None:
        payload = dict(self.base_payload())
        payload["channel"] = "dry_run"
        payload["autonomy_level"] = "level_1_campaign_package"

        adapter = DryRunAdapter(audit_log=self.audit)
        result = adapter.publish(payload)

        self.assertTrue(result["ok"])
        self.assertEqual(result["side_effects"], "none")
        self.assertTrue(self.audit_path.exists())

    def test_test_page_adapter_writes_local_jsonl_only(self) -> None:
        adapter = TestPageAdapter(output_path=self.test_page_path, audit_log=self.audit)
        result = adapter.publish(self.base_payload())

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "published_to_test_page")
        self.assertTrue(self.test_page_path.exists())

        lines = self.test_page_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["side_effects"], "local_jsonl_only")
        self.assertEqual(record["channel"], "test_page")

    def test_plaintext_token_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["access_token"] = "plain-text-token-forbidden"

        decision, reasons = evaluate_permission("test_page", "level_2_sandbox_page", payload)

        self.assertEqual(decision, PermissionDecision.DENY)
        self.assertTrue(any(reason.startswith("plaintext_secret_blocked") for reason in reasons))

    def test_official_real_publish_is_blocked(self) -> None:
        payload = self.base_payload()
        payload.update({
            "channel": "instagram_official",
            "autonomy_level": "level_4_limited_real_publish",
            "external_api_used": True,
            "publish_real": True,
            "credential_vault_ref": "vault://instagram/test-account",
        })

        queue = PublishQueue(path=self.queue_path, audit_log=self.audit)
        item = queue.enqueue(payload)

        self.assertEqual(item["status"], ApprovalStatus.BLOCKED.value)
        self.assertIn("real_publish_not_allowed", ",".join(item["approval"]["reasons"]))

    def test_queue_blocks_mass_messaging_and_browser_automation(self) -> None:
        payload = self.base_payload()
        payload["mass_messaging"] = True
        payload["browser_automation"] = True

        queue = PublishQueue(path=self.queue_path, audit_log=self.audit)
        item = queue.enqueue(payload)

        self.assertEqual(item["status"], ApprovalStatus.BLOCKED.value)
        reasons = ",".join(item["approval"]["reasons"])
        self.assertIn("mass_messaging_blocked", reasons)
        self.assertIn("browser_automation_blocked", reasons)

    def test_queue_keeps_pending_review_when_approval_is_missing(self) -> None:
        payload = self.base_payload()
        payload["human_approval"] = {"approved": False, "reviewer": ""}

        queue = PublishQueue(path=self.queue_path, audit_log=self.audit)
        item = queue.enqueue(payload)

        self.assertEqual(item["status"], ApprovalStatus.PENDING_HUMAN_REVIEW.value)
        self.assertTrue(self.queue_path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)