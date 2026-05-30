from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_os_mvp_readiness.readiness import LocalOSMVPReadiness


class LocalOSMVPReadinessSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_local_os_mvp_"))
        readiness = LocalOSMVPReadiness(project_root=self.tmp)
        for item in readiness.components():
            (self.tmp / item["module"]).mkdir(parents=True, exist_ok=True)
            page = self.tmp / item["page"]
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text("# demo page\n", encoding="utf-8")
        self.readiness = LocalOSMVPReadiness(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_report_ready(self) -> None:
        report = self.readiness.build_report()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "99")
        self.assertTrue(report["summary"]["local_os_ready"])
        self.assertEqual(report["summary"]["readiness_score"], 100.0)

    def test_report_files_created(self) -> None:
        self.readiness.build_report()
        self.assertTrue((self.tmp / "reports" / "local_os_mvp_readiness" / "latest_local_os_mvp_readiness.json").exists())
        self.assertTrue((self.tmp / "reports" / "local_os_mvp_readiness" / "latest_local_os_mvp_readiness.md").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/99_K_Atlas_Local_OS_MVP_Readiness.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
