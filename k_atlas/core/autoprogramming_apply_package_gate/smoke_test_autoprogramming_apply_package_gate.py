from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autoprogramming_apply_package_gate.gate import AutoprogrammingApplyPackageGate
from k_atlas.core.autoprogramming_apply_package_gate.policy import validate_apply_package


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class AutoprogrammingApplyPackageGateSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_apply_package_gate_"))
        self.package_queue_path = self.tmp / "live" / "builder" / "apply_package_queue.json"
        self.package_queue_path.parent.mkdir(parents=True, exist_ok=True)

        content = "demo seguro"

        packages = [
            {
                "apply_package_id": "package-1",
                "source_review_id": "review-1",
                "source_proposal_id": "proposal-1",
                "checkpoint": "68",
                "objective": "Criar modulo seguro.",
                "status": "waiting_execution_gate_validation",
                "file_plans": [
                    {
                        "action": "create_module",
                        "path": "k_atlas/core/demo/README.md",
                        "purpose": "teste",
                        "content": content,
                        "content_sha256": sha(content),
                    }
                ],
                "package_hash": "package-hash-demo",
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_api_enabled": False,
                "auto_publish": False,
                "auto_send": False,
                "auto_deploy": False,
                "browser_automation": False,
                "mouse_automation": False,
                "apply_now": False,
            }
        ]

        self.package_queue_path.write_text(
            json.dumps(packages, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.gate = AutoprogrammingApplyPackageGate(
            package_queue_path=self.package_queue_path,
            live_dir=self.tmp / "live" / "gate",
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_validate_package_blocks_real_execution(self) -> None:
        result = validate_apply_package({
            "apply_package_id": "x",
            "status": "waiting_execution_gate_validation",
            "file_plans": [],
            "package_hash": "hash",
            "real_execution_enabled": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("real_execution_enabled_blocked", result["reasons"])

    def test_build_gate_queue(self) -> None:
        result = self.gate.build_gate_queue()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "68")
        self.assertEqual(result["summary"]["gate_items_created"], 1)
        self.assertEqual(result["summary"]["waiting_human_apply_approval"], 1)
        self.assertFalse(result["summary"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "gate" / "apply_package_gate_queue.json").exists())
        self.assertTrue((self.tmp / "reports" / "latest_autoprogramming_apply_package_gate.json").exists())

    def test_idempotent(self) -> None:
        first = self.gate.build_gate_queue()
        second = self.gate.build_gate_queue()

        self.assertEqual(first["summary"]["gate_items_created"], 1)
        self.assertEqual(second["summary"]["gate_items_created"], 0)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/68_K_Atlas_Autoprogramming_Apply_Package_Gate.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
