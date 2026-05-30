from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.manual_apply_executor.executor import ManualApplyExecutor
from k_atlas.core.manual_apply_executor.policy import validate_manual_apply_request


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ManualApplyExecutorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_manual_apply_"))
        self.gate_queue_path = self.tmp / "live" / "gate" / "apply_package_gate_queue.json"
        self.gate_queue_path.parent.mkdir(parents=True, exist_ok=True)

        content = "# Demo seguro\n"

        gate_items = [
            {
                "gate_id": "gate-1",
                "apply_package_id": "package-1",
                "checkpoint": "69",
                "objective": "Criar arquivo demo seguro.",
                "status": "waiting_human_apply_approval",
                "manual_apply_allowed_after_approval": True,
                "automatic_apply_allowed": False,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "validation": {
                    "ok": True,
                    "status": "apply_package_gate_passed",
                },
                "package_snapshot": {
                    "file_plans": [
                        {
                            "path": "k_atlas/core/demo_manual_apply/README.md",
                            "content": content,
                            "content_sha256": sha(content),
                        }
                    ]
                },
            }
        ]

        self.gate_queue_path.write_text(
            json.dumps(gate_items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.executor = ManualApplyExecutor(
            project_root=self.tmp,
            gate_queue_path=self.gate_queue_path.relative_to(self.tmp),
            memory_dir="memory/manual_apply_executor",
            reports_dir="reports/manual_apply_executor",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_requires_human_approval(self) -> None:
        result = validate_manual_apply_request({
            "apply_mode": "manual",
            "human_approved": False,
        })

        self.assertFalse(result["ok"])
        self.assertIn("human_approval_required", result["reasons"])

    def test_dry_run(self) -> None:
        result = self.executor.dry_run()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "69")
        self.assertEqual(result["summary"]["planned_files"], 1)
        self.assertFalse(result["summary"]["real_execution_enabled"])

    def test_manual_apply_with_backup_manifest(self) -> None:
        target = self.tmp / "k_atlas" / "core" / "demo_manual_apply" / "README.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("old", encoding="utf-8")

        result = self.executor.apply_manual({
            "human_approved": True,
            "apply_mode": "manual",
            "notes": "teste supervisionado",
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "manual_apply_completed")
        self.assertTrue(target.exists())
        self.assertIn("Demo seguro", target.read_text(encoding="utf-8"))
        self.assertTrue((self.tmp / "memory" / "manual_apply_executor" / "apply_manifest.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/69_K_Atlas_Manual_Apply_Executor.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
