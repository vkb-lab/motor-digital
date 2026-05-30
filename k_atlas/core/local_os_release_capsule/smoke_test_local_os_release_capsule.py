from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_os_mvp_readiness.readiness import LocalOSMVPReadiness
from k_atlas.core.local_os_release_capsule.capsule import LocalOSReleaseCapsule


class LocalOSReleaseCapsuleSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_local_os_capsule_"))
        readiness = LocalOSMVPReadiness(project_root=self.tmp)
        for item in readiness.components():
            (self.tmp / item["module"]).mkdir(parents=True, exist_ok=True)
            page = self.tmp / item["page"]
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text("# demo page\n", encoding="utf-8")
        self.capsule = LocalOSReleaseCapsule(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_capsule(self) -> None:
        report = self.capsule.build_capsule()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "100")
        self.assertEqual(report["status"], "release_candidate_ready")
        self.assertEqual(report["version"], "0.1.0-local-os-mvp")

    def test_report_files_created(self) -> None:
        self.capsule.build_capsule()
        self.assertTrue((self.tmp / "reports" / "local_os_release_capsule" / "latest_local_os_release_capsule.json").exists())
        self.assertTrue((self.tmp / "reports" / "local_os_release_capsule" / "latest_local_os_release_capsule.md").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/100_K_Atlas_Local_OS_Release_Capsule.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
