from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.assisted_autoprogramming.kernel import AssistedAutoprogrammingKernel
from k_atlas.core.assisted_autoprogramming.policy import validate_autoprog_request, validate_file_plan


class AssistedAutoprogrammingSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_autoprog_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_external_execution(self) -> None:
        result = validate_autoprog_request({
            "checkpoint": "65",
            "action": "create_module",
            "objective": "teste",
            "external_api_enabled": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("external_api_enabled_blocked", result["reasons"])

    def test_file_plan_blocks_absolute_path(self) -> None:
        result = validate_file_plan({
            "action": "create_module",
            "path": "C:/danger/file.py",
            "content": "x = 1",
        })
        self.assertFalse(result["ok"])

    def test_create_proposal(self) -> None:
        kernel = AssistedAutoprogrammingKernel(
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
            package_dir=self.tmp / "live",
        )

        result = kernel.create_proposal({
            "checkpoint": "65",
            "action": "create_module",
            "objective": "Criar proposta segura de autoprogramacao assistida.",
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "65")
        self.assertEqual(result["status"], "proposal_created")
        self.assertFalse(result["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "memory" / "proposal_queue.json").exists())
        self.assertTrue((self.tmp / "live" / "autoprog_package_queue.json").exists())
        self.assertTrue((self.tmp / "reports" / "latest_assisted_autoprogramming.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_assisted_autoprogramming.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "65")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/65_K_Atlas_Assisted_Autoprogramming.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
