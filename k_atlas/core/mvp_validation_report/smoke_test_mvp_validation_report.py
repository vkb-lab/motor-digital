from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.mvp_validation_report.validation import MVPValidationReport


class MVPValidationReportSmokeTest(unittest.TestCase):
    def test_build_report(self) -> None:
        report = MVPValidationReport().build_report()
        self.assertEqual(report["checkpoint"], "105")
        self.assertFalse(report["summary"]["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/105_K_Atlas_MVP_Validation_Report.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
