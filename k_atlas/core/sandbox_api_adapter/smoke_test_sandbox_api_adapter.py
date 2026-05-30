from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.sandbox_api_adapter.adapter import SandboxAPIAdapter
from k_atlas.core.sandbox_api_adapter.audit import SandboxAPIAuditLog
from k_atlas.core.sandbox_api_adapter.policy import validate_sandbox_api_payload
from k_atlas.core.sandbox_api_adapter.providers import build_provider_registry


class SandboxAPIAdapterSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_sandbox_api_"))
        self.audit = SandboxAPIAuditLog(self.tmp / "requests.json")
        self.adapter = SandboxAPIAdapter(self.audit)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_provider_registry(self) -> None:
        providers = build_provider_registry()
        self.assertIn("google_ai_sandbox", providers)
        self.assertIn("meta_graph_sandbox", providers)
        self.assertIn("whatsapp_cloud_sandbox", providers)

    def test_policy_blocks_real_network(self) -> None:
        result = validate_sandbox_api_payload({"real_network": True})
        self.assertFalse(result["ok"])
        self.assertIn("real_network_blocked_in_sandbox", result["reasons"])

    def test_policy_blocks_plaintext_secret(self) -> None:
        result = validate_sandbox_api_payload({"api_key": "plain-secret"})
        self.assertFalse(result["ok"])

    def test_execute_google_sandbox(self) -> None:
        result = self.adapter.execute(
            provider_id="google_ai_sandbox",
            operation="plan_video_generation",
            payload={
                "objective": "Gerar vídeo do K-Atlas",
                "external_api_enabled": False,
                "official_publish": False,
                "real_network": False,
            },
            requested_by="smoke_test",
        )

        self.assertTrue(result["ok"])
        self.assertFalse(result["network_used"])
        self.assertEqual(len(self.audit.load()), 1)

    def test_blocks_unsupported_provider(self) -> None:
        result = self.adapter.execute("unknown", "test", {}, requested_by="smoke_test")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "provider_not_registered")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/17_K_Atlas_Sandbox_API_Adapter.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
