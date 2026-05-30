from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_os_health_check.health import LocalOSHealthCheck


class LocalOSHealthCheckSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_health_"))
        (self.tmp / "k_atlas/core/local_mission_installer").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_collect(self) -> None:
        report = LocalOSHealthCheck(project_root=self.tmp).collect()
        self.assertEqual(report["checkpoint"], "101")
        self.assertIn("readiness", report["summary"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/101_K_Atlas_Local_OS_Health_Check.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
