from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autoprogramming_apply_package_builder.builder import AutoprogrammingApplyPackageBuilder
from k_atlas.core.autoprogramming_apply_package_builder.policy import validate_apply_package_request


class AutoprogrammingApplyPackageBuilderSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_apply_package_builder_"))
        self.review_queue_path = self.tmp / "live" / "reviewer" / "proposal_review_queue.json"
        self.review_queue_path.parent.mkdir(parents=True, exist_ok=True)

        reviews = [
            {
                "review_id": "review-1",
                "proposal_id": "proposal-1",
                "checkpoint": "67",
                "objective": "Criar modulo seguro.",
                "status": "decided",
                "decision": {
                    "decision": "approve_for_apply_package",
                    "apply_package_enabled": True,
                    "real_execution_enabled": False,
                },
                "execution_enabled": False,
                "real_execution_enabled": False,
                "proposal_snapshot": {
                    "file_plans": [
                        {
                            "action": "create_module",
                            "path": "k_atlas/core/demo/README.md",
                            "purpose": "teste",
                            "content": "demo seguro",
                        }
                    ]
                },
            }
        ]

        self.review_queue_path.write_text(
            json.dumps(reviews, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.builder = AutoprogrammingApplyPackageBuilder(
            review_queue_path=self.review_queue_path,
            live_dir=self.tmp / "live" / "builder",
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_apply_now(self) -> None:
        result = validate_apply_package_request({
            "apply_now": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("apply_now_blocked", result["reasons"])

    def test_build_apply_packages(self) -> None:
        result = self.builder.build_apply_packages({
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "67")
        self.assertEqual(result["summary"]["packages_created"], 1)
        self.assertFalse(result["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "builder" / "apply_package_queue.json").exists())
        self.assertTrue((self.tmp / "reports" / "latest_autoprogramming_apply_package_builder.json").exists())

        package = result["created_packages"][0]
        self.assertEqual(package["status"], "waiting_execution_gate_validation")
        self.assertFalse(package["execution_enabled"])
        self.assertFalse(package["real_execution_enabled"])

    def test_idempotent(self) -> None:
        first = self.builder.build_apply_packages()
        second = self.builder.build_apply_packages()

        self.assertEqual(first["summary"]["packages_created"], 1)
        self.assertEqual(second["summary"]["packages_created"], 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/67_K_Atlas_Autoprogramming_Apply_Package_Builder.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
