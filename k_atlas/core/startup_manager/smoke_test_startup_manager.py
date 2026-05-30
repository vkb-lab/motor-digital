from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.startup_manager.manager import StartupManager


class StartupManagerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_startup_"))
        target = self.tmp / "pages/104_K_Atlas_Operator_Home.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("print('demo')", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_config(self) -> None:
        report = StartupManager(project_root=self.tmp).build_config()
        self.assertEqual(report["checkpoint"], "102")
        self.assertFalse(report["summary"]["autostart_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/102_K_Atlas_Startup_Manager.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
