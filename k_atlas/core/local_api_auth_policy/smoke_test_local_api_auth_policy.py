from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.local_api_auth_policy.policy import validate_local_api_runtime_request


class LocalApiAuthPolicySmokeTest(unittest.TestCase):
    def test_allows_localhost(self) -> None:
        result = validate_local_api_runtime_request({"bind_host": "127.0.0.1", "port": 8787})
        self.assertTrue(result["ok"])

    def test_blocks_public_host(self) -> None:
        result = validate_local_api_runtime_request({"bind_host": "0.0.0.0", "port": 8787})
        self.assertFalse(result["ok"])
        self.assertIn("public_bind_host_blocked:0.0.0.0", result["reasons"])

    def test_blocks_auto_execute(self) -> None:
        result = validate_local_api_runtime_request({"bind_host": "127.0.0.1", "auto_execute": True})
        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/90_K_Atlas_Local_API_Auth_Policy.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
