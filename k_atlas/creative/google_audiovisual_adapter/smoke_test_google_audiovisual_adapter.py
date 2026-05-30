from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.ai_provider_router.router import AIProviderRouter
from k_atlas.creative.google_audiovisual_adapter.policy import validate_audiovisual_payload
from k_atlas.creative.google_audiovisual_adapter.sandbox import GoogleAudiovisualAdapterSandbox


class GoogleAudiovisualAdapterSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_google_av_adapter_"))
        self.router = AIProviderRouter(
            reports_dir=self.tmp / "router_reports",
            memory_dir=self.tmp / "router_memory",
        )
        self.adapter = GoogleAudiovisualAdapterSandbox(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
            router=self.router,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_live_call(self) -> None:
        payload = self.adapter.default_payload()
        payload["live_call"] = True
        result = validate_audiovisual_payload(payload)
        self.assertFalse(result["ok"])
        self.assertIn("live_call_blocked", result["reasons"])

    def test_generate_sandbox(self) -> None:
        result = self.adapter.generate()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "51")
        self.assertFalse(result["live_call_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_google_audiovisual_adapter_sandbox.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_google_audiovisual_adapter_sandbox.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "51")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/32_K_Atlas_Google_Audiovisual_Sandbox.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
