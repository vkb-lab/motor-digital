from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.security.credential_vault import (
    VaultResolutionError,
    is_vault_ref,
    resolve_secret,
    validate_no_plaintext_secrets,
)

from k_atlas.social.publishing_gateway.audit_log import AuditLog
from k_atlas.social.publishing_gateway.test_page_api_adapter import TestPageAPIAdapter


class Stage7IndependenceSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_stage7_"))
        self.audit = AuditLog(self.tmp / "audit.jsonl")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.environ.pop("K_SOCIAL_TEST_PAGE_ENDPOINT", None)
        os.environ.pop("K_SOCIAL_TEST_PAGE_TOKEN", None)
        os.environ.pop("K_SOCIAL_EXTERNAL_API_ENABLED", None)
        os.environ.pop("K_SOCIAL_AUTO_PUBLISH", None)

    def payload(self) -> dict:
        return {
            "campaign_id": "parada-atlantida-ecobier-futebol-2026",
            "channel": "test_page",
            "autonomy_level": "level_2_5_test_adapter",
            "content": {
                "title": "Parada Atlantida + Chopp Ecobier",
                "body": "Validacao controlada para pagina de teste.",
                "cta": "Validar criativo",
            },
            "human_approval": {
                "approved": True,
                "reviewer": "k_atlas_engineer",
            },
            "external_api_used": True,
            "publish_real": False,
            "mass_messaging": False,
            "browser_automation": False,
        }

    def test_vault_ref_detection(self) -> None:
        self.assertTrue(is_vault_ref("vault://env/K_SOCIAL_TEST_PAGE_TOKEN"))
        self.assertFalse(is_vault_ref("plain-token"))

    def test_vault_resolves_env_secret(self) -> None:
        os.environ["K_SOCIAL_TEST_PAGE_TOKEN"] = "test-token"
        self.assertEqual(resolve_secret("vault://env/K_SOCIAL_TEST_PAGE_TOKEN"), "test-token")

    def test_vault_blocks_missing_secret(self) -> None:
        with self.assertRaises(VaultResolutionError):
            resolve_secret("vault://env/K_SOCIAL_TEST_PAGE_TOKEN")

    def test_plaintext_secret_is_blocked(self) -> None:
        payload = self.payload()
        payload["access_token"] = "plain-text-token"
        result = validate_no_plaintext_secrets(payload)

        self.assertFalse(result.ok)
        self.assertIn("plaintext_secret_blocked", result.reasons[0])

    def test_api_adapter_blocks_when_external_api_disabled(self) -> None:
        os.environ["K_SOCIAL_EXTERNAL_API_ENABLED"] = "false"

        adapter = TestPageAPIAdapter(audit_log=self.audit)
        result = adapter.publish(self.payload())

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "external_api_disabled")
        self.assertEqual(result["side_effects"], "none")

    def test_api_adapter_requires_vault_when_enabled(self) -> None:
        os.environ["K_SOCIAL_EXTERNAL_API_ENABLED"] = "true"
        os.environ["K_SOCIAL_AUTO_PUBLISH"] = "false"

        adapter = TestPageAPIAdapter(audit_log=self.audit)
        result = adapter.publish(self.payload())

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "missing_vault_secret")
        self.assertEqual(result["side_effects"], "none")

    def test_api_adapter_blocks_real_publish(self) -> None:
        payload = self.payload()
        payload["publish_real"] = True

        adapter = TestPageAPIAdapter(audit_log=self.audit)
        result = adapter.publish(payload)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "real_publish_blocked")


if __name__ == "__main__":
    unittest.main(verbosity=2)