from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.publishing_gateway.audit_log import AuditLog
from k_atlas.social.publishing_gateway.instagram_level4_adapter import InstagramLevel4Adapter


class InstagramLevel4AdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ig_l4_adapter_"))
        self.audit = AuditLog(self.tmp / "audit.jsonl")
        self.adapter = InstagramLevel4Adapter(audit_log=self.audit)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def base_payload(self) -> dict:
        return {
            "client_id": "kos_viking",
            "account_alias": "kos_viking",
            "channel": "instagram_official",
            "autonomy_level": "level_4_limited_real_publish",
            "campaign_name": "kos_base_test",
            "image_url": "https://placehold.co/1080x1080/png",
            "caption": "K-OS BASE preview.",
            "publish_real": False,
            "browser_automation": False,
            "mass_messaging": False,
        }

    def test_preview_has_no_external_side_effects(self) -> None:
        result = self.adapter.prepare(self.base_payload())

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ready_for_level4_preview")
        self.assertEqual(result["side_effects"], "none")

    def test_hupmix_test_account_is_allowlisted(self) -> None:
        payload = self.base_payload()
        payload["client_id"] = "hupmix"
        payload["account_alias"] = "hupmix"

        result = self.adapter.prepare(payload)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ready_for_level4_preview")

    def test_production_client_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["client_id"] = "parada_atlantida"

        result = self.adapter.prepare(payload)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "blocked_by_instagram_level4_policy")
        self.assertIn("client_blocked_for_real_publish:parada_atlantida", result["reasons"])

    def test_publish_real_requires_execute_switch(self) -> None:
        payload = self.base_payload()
        payload["publish_real"] = True

        result = self.adapter.publish(payload, execute_real_confirmed=False)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "blocked_by_execute_switch")
        self.assertEqual(result["side_effects"], "none")

    def test_plaintext_secret_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["access_token"] = "plain-text-token"

        result = self.adapter.prepare(payload)

        self.assertFalse(result["ok"])
        self.assertTrue(any(reason.startswith("plaintext_secret_blocked") for reason in result["reasons"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
