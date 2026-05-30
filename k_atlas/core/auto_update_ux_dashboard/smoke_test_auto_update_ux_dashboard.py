from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.auto_update_ux_dashboard.dashboard import AutoUpdateUXDashboard
from k_atlas.core.download_cleanup_policy.policy import DownloadCleanupPolicy
from k_atlas.core.operator_clipboard_return.clipboard_return import OperatorClipboardReturn


class AutoUpdateUXDashboardSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_auto_update_ux_"))
        memory = self.tmp / "memory" / "auto_update_watcher"
        memory.mkdir(parents=True, exist_ok=True)
        (memory / "events.jsonl").write_text(
            json.dumps({"event_type": "installer_ok", "payload": {"file": "demo"}}) + "\n",
            encoding="utf-8",
        )
        (memory / "latest_run.log").write_text("demo ok", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_dashboard_builds(self) -> None:
        report = AutoUpdateUXDashboard(project_root=self.tmp).build_report()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "122")
        self.assertEqual(report["status"], "operational")
        self.assertTrue((self.tmp / "reports" / "auto_update_ux_dashboard" / "latest_auto_update_ux_dashboard.json").exists())

    def test_cleanup_policy_read_only(self) -> None:
        report = DownloadCleanupPolicy(project_root=self.tmp, downloads_dir=self.tmp / "Downloads").build_report()
        self.assertTrue(report["ok"])
        self.assertFalse(report["summary"]["delete_mode_enabled"])

    def test_clipboard_return(self) -> None:
        result = OperatorClipboardReturn(project_root=self.tmp).build_return("ok", "test")
        self.assertEqual(result["clipboard_text"], "ok")

    def test_pages_compile(self) -> None:
        pages = [
            "pages/118_K_Atlas_Silent_Update_Status_Center.py",
            "pages/119_K_Atlas_Auto_Update_Notification_Bridge.py",
            "pages/120_K_Atlas_Download_Cleanup_Policy.py",
            "pages/121_K_Atlas_Operator_Clipboard_Return.py",
            "pages/122_K_Atlas_Auto_Update_UX_Dashboard.py",
        ]
        for page in pages:
            py_compile.compile(page, doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
