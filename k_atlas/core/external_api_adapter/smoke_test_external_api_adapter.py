from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.external_api_adapter.policy import validate_external_api_payload
from k_atlas.core.external_api_adapter.readiness import ExternalAPIAdapterReadiness


class ExternalAPIAdapterSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_external_api_adapter_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_plaintext_token(self) -> None:
        result = validate_external_api_payload({
            "provider": "openai",
            "token": "abc",
            "env_vars": ["OPENAI_API_KEY"],
        })

        self.assertFalse(result["ok"])
        self.assertIn("plaintext_token_blocked", result["reasons"])

    def test_policy_blocks_env_value(self) -> None:
        result = validate_external_api_payload({
            "provider": "openai",
            "env_vars": ["OPENAI_API_KEY=abc"],
        })

        self.assertFalse(result["ok"])
        self.assertIn("env_var_must_not_contain_value", result["reasons"])

    def test_generate_readiness(self) -> None:
        readiness = ExternalAPIAdapterReadiness(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        result = readiness.generate()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "49")
        self.assertFalse(result["summary"]["live_external_calls_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_external_api_adapter_readiness.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_external_api_adapter_readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "49")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/30_K_Atlas_External_API_Readiness.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
