from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.ai_provider_router.policy import validate_router_payload
from k_atlas.core.ai_provider_router.router import AIProviderRouter


class AIProviderRouterSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_ai_router_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_live_call(self) -> None:
        result = validate_router_payload({
            "task_type": "video_generation",
            "live_call": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("live_call_blocked", result["reasons"])

    def test_policy_blocks_plaintext_token(self) -> None:
        result = validate_router_payload({
            "task_type": "text_reasoning",
            "token": "abc",
        })

        self.assertFalse(result["ok"])
        self.assertIn("plaintext_token_blocked", result["reasons"])

    def test_route_video_generation(self) -> None:
        router = AIProviderRouter(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        result = router.route({
            "task_type": "video_generation",
            "objective": "teste audiovisual",
            "live_call": False,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "50")
        self.assertEqual(result["task_type"], "video_generation")
        self.assertTrue((self.tmp / "reports" / "latest_ai_provider_router.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_ai_provider_router.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "50")

    def test_matrix(self) -> None:
        router = AIProviderRouter(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        matrix = router.build_matrix()

        self.assertTrue(matrix["ok"])
        self.assertGreaterEqual(len(matrix["routes"]), 5)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/31_K_Atlas_AI_Provider_Router.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
