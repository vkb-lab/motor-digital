from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.supervised_autonomy_dashboard.dashboard import SupervisedAutonomyDashboard


class SupervisedAutonomyDashboardSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_supervised_dashboard_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_report(self) -> None:
        dashboard = SupervisedAutonomyDashboard(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )
        result = dashboard.build_report()
        self.assertEqual(result["checkpoint"], "98")
        self.assertIn(result["status"], {"operational", "attention_required"})
        self.assertFalse(result["summary"]["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/98_K_Atlas_Supervised_Autonomy_Dashboard.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
