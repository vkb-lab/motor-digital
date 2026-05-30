from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.manual_apply_rollback_executor.policy import validate_manual_rollback_request
from k_atlas.core.manual_apply_rollback_executor.rollback import ManualApplyRollbackExecutor


class ManualApplyRollbackExecutorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_manual_rollback_"))

        target_restore = self.tmp / "k_atlas" / "core" / "rollback_demo" / "README.md"
        target_restore.parent.mkdir(parents=True, exist_ok=True)
        target_restore.write_text("new content", encoding="utf-8")

        backup = self.tmp / "memory" / "manual_apply_executor" / "runs" / "run-1" / "backups" / "readme_backup"
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text("old content", encoding="utf-8")

        target_delete = self.tmp / "k_atlas" / "core" / "rollback_demo" / "CREATED.md"
        target_delete.write_text("created content", encoding="utf-8")

        manifest = [
            {
                "run_id": "run-1",
                "rollback_available": True,
                "applied_files": [
                    {
                        "path": "k_atlas/core/rollback_demo/README.md",
                        "backup_path": str(backup),
                    },
                    {
                        "path": "k_atlas/core/rollback_demo/CREATED.md",
                        "backup_path": None,
                    },
                ],
            }
        ]

        manifest_path = self.tmp / "memory" / "manual_apply_executor" / "apply_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        self.executor = ManualApplyRollbackExecutor(
            project_root=self.tmp,
            apply_manifest_path="memory/manual_apply_executor/apply_manifest.json",
            memory_dir="memory/manual_apply_rollback_executor",
            reports_dir="reports/manual_apply_rollback_executor",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_requires_human_approval(self) -> None:
        result = validate_manual_rollback_request({
            "human_approved": False,
            "rollback_mode": "manual",
        })

        self.assertFalse(result["ok"])
        self.assertIn("human_approval_required", result["reasons"])

    def test_dry_run(self) -> None:
        result = self.executor.dry_run()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "70")
        self.assertEqual(result["summary"]["planned_files"], 2)

    def test_manual_rollback(self) -> None:
        result = self.executor.rollback_manual({
            "human_approved": True,
            "rollback_mode": "manual",
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "manual_rollback_completed")

        restored = self.tmp / "k_atlas" / "core" / "rollback_demo" / "README.md"
        deleted = self.tmp / "k_atlas" / "core" / "rollback_demo" / "CREATED.md"

        self.assertEqual(restored.read_text(encoding="utf-8"), "old content")
        self.assertFalse(deleted.exists())
        self.assertTrue((self.tmp / "memory" / "manual_apply_rollback_executor" / "rollback_manifest.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/70_K_Atlas_Manual_Apply_Rollback_Executor.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
