from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.secure_local_api_readiness.api import SecureLocalApiReadiness
from k_atlas.core.secure_local_api_readiness.policy import validate_local_api_request


class SecureLocalApiReadinessSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_api_readiness_"))
        self.api = SecureLocalApiReadiness(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_public(self) -> None:
        result = validate_local_api_request({"mode": "readiness", "public_exposure": True})
        self.assertFalse(result["ok"])
        self.assertIn("public_exposure_blocked", result["reasons"])

    def test_report(self) -> None:
        result = self.api.build_report({"mode": "readiness", "bind_address": "127.0.0.1"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "79")
        self.assertFalse(result["real_execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "secure_local_api_readiness" / "latest_secure_local_api_readiness.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/79_K_Atlas_Secure_Local_API_Readiness.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
