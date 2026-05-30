from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.whatsapp_cloud_readiness.policy import validate_whatsapp_payload
from k_atlas.social.whatsapp_cloud_readiness.readiness import WhatsAppCloudReadiness


class WhatsAppCloudReadinessSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_whatsapp_cloud_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_access_token(self) -> None:
        result = validate_whatsapp_payload({
            "objective": "readiness",
            "access_token": "abc",
            "env_vars": ["WHATSAPP_ACCESS_TOKEN"],
        })

        self.assertFalse(result["ok"])
        self.assertIn("plaintext_access_token_blocked", result["reasons"])

    def test_policy_blocks_auto_send(self) -> None:
        result = validate_whatsapp_payload({
            "objective": "readiness",
            "auto_send": True,
            "env_vars": ["WHATSAPP_ACCESS_TOKEN"],
        })

        self.assertFalse(result["ok"])
        self.assertIn("auto_send_blocked", result["reasons"])

    def test_generate_readiness(self) -> None:
        readiness = WhatsAppCloudReadiness(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        result = readiness.generate()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "53")
        self.assertFalse(result["summary"]["live_call_enabled"])
        self.assertFalse(result["summary"]["message_send_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_whatsapp_cloud_readiness.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_whatsapp_cloud_readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "53")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/34_K_Atlas_WhatsApp_Cloud_Readiness.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
