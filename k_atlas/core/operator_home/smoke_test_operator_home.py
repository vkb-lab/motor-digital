from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.operator_home.home import OperatorHome


class OperatorHomeSmokeTest(unittest.TestCase):
    def test_build_home(self) -> None:
        report = OperatorHome().build_home()
        self.assertEqual(report["checkpoint"], "104")
        self.assertFalse(report["summary"]["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/104_K_Atlas_Operator_Home.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
