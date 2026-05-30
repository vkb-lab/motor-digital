from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.download_intake_ux.manager import DownloadIntakeUX


class DownloadIntakeUXSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_download_intake_ux_"))
        state_dir = self.tmp / "memory" / "download_intake"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "state.json").write_text(
            '{"fixed_command": "cd test; powershell -File .\\\\ops\\\\k_next.ps1"}',
            encoding="utf-8",
        )
        self.manager = DownloadIntakeUX(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_summary(self) -> None:
        report = self.manager.summary()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "106")
        self.assertEqual(report["status"], "operational")
        self.assertTrue(report["summary"]["fixed_command_available"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/106_K_Atlas_Download_Intake_UX.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
