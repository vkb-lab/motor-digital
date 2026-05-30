from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.daily_operator.cockpit import DailyOperatorCockpit


class DailyOperatorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_daily_operator_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_collect_report(self) -> None:
        cockpit = DailyOperatorCockpit(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        result = cockpit.collect()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "48")
        self.assertTrue((self.tmp / "reports" / "latest_daily_operator_cockpit.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_daily_operator_cockpit.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "48")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/29_K_Atlas_Daily_Operator_Cockpit.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
