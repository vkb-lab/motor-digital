from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.instagram_graph_readiness.policy import validate_instagram_payload
from k_atlas.social.instagram_graph_readiness.readiness import InstagramGraphReadiness


class InstagramGraphReadinessSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_instagram_graph_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_access_token(self) -> None:
        result = validate_instagram_payload({
            "objective": "readiness",
            "access_token": "abc",
            "env_vars": ["META_ACCESS_TOKEN"],
        })

        self.assertFalse(result["ok"])
        self.assertIn("plaintext_access_token_blocked", result["reasons"])

    def test_policy_blocks_live_call(self) -> None:
        result = validate_instagram_payload({
            "objective": "readiness",
            "live_call": True,
            "env_vars": ["META_ACCESS_TOKEN"],
        })

        self.assertFalse(result["ok"])
        self.assertIn("live_call_blocked", result["reasons"])

    def test_generate_readiness(self) -> None:
        readiness = InstagramGraphReadiness(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        result = readiness.generate()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "52")
        self.assertFalse(result["summary"]["live_call_enabled"])
        self.assertFalse(result["summary"]["publishing_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_instagram_graph_readiness.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_instagram_graph_readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "52")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/33_K_Atlas_Instagram_Graph_Readiness.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
