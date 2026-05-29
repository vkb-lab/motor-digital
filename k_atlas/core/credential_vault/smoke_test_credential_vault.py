from __future__ import annotations

import os
import unittest

from k_atlas.core.credential_vault.env_contract import build_env_contract
from k_atlas.core.credential_vault.policy import mask_secret, validate_secret_payload
from k_atlas.core.credential_vault.vault import CredentialVault


class CredentialVaultSmokeTest(unittest.TestCase):
    def test_mask_secret(self) -> None:
        masked = mask_secret("abcd1234efgh")
        self.assertTrue(masked.startswith("abcd"))
        self.assertTrue(masked.endswith("efgh"))
        self.assertNotIn("1234", masked)

    def test_blocks_plaintext_secret(self) -> None:
        result = validate_secret_payload({
            "api_key": "plaintext-secret",
        })

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "blocked_plaintext_secret")

    def test_allows_vault_ref(self) -> None:
        result = validate_secret_payload({
            "api_key": "vault://env/GOOGLE_AI_API_KEY",
        })

        self.assertTrue(result["ok"])

    def test_vault_ref_parsing(self) -> None:
        vault = CredentialVault()
        self.assertEqual(vault.parse_ref("vault://env/GOOGLE_AI_API_KEY"), "GOOGLE_AI_API_KEY")

    def test_vault_inspects_env_without_exposing(self) -> None:
        os.environ["K_ATLAS_TEST_SECRET"] = "abcd1234efgh"
        vault = CredentialVault()
        result = vault.require_ref("vault://env/K_ATLAS_TEST_SECRET")

        self.assertTrue(result["ok"])
        self.assertNotEqual(result["credential"]["masked_preview"], "abcd1234efgh")
        self.assertIn("*", result["credential"]["masked_preview"])

    def test_env_contract(self) -> None:
        contract = build_env_contract()
        self.assertEqual(contract["checkpoint"], "35")
        self.assertIn("future_optional", contract)


if __name__ == "__main__":
    unittest.main(verbosity=2)
