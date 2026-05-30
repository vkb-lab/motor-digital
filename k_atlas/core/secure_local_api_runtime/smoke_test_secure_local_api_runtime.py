from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.secure_local_api_runtime.runtime import SecureLocalApiRuntime


class SecureLocalApiRuntimeSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_secure_api_"))
        self.runtime = SecureLocalApiRuntime(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_config(self) -> None:
        config = self.runtime.build_config()
        self.assertTrue(config["ok"])
        self.assertEqual(config["host"], "127.0.0.1")
        self.assertFalse(config["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "secure_local_api_runtime" / "server_config.json").exists())

    def test_status(self) -> None:
        status = self.runtime.status()
        self.assertTrue(status["ok"])
        self.assertEqual(status["checkpoint"], "89")

    def test_server_compiles(self) -> None:
        py_compile.compile("k_atlas/core/secure_local_api_runtime/server.py", doraise=True)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/89_K_Atlas_Secure_Local_API_Runtime.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
