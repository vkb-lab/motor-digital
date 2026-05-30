from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.one_click_launcher.launcher import OneClickLauncher


class OneClickLauncherSmokeTest(unittest.TestCase):
    def test_build_launch_plan(self) -> None:
        report = OneClickLauncher().build_launch_plan()
        self.assertEqual(report["checkpoint"], "103")
        self.assertFalse(report["summary"]["automatic_launch_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/103_K_Atlas_One_Click_Launcher.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
