from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autoreporter.report_builder import AutoReporterCentral
from k_atlas.core.autoreporter.snapshot import build_system_snapshot


class AutoReporterCentralSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_autoreporter_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapshot(self) -> None:
        snapshot = build_system_snapshot()
        self.assertEqual(snapshot["project"], "K-Atlas OS")
        self.assertIn("modules", snapshot)
        self.assertIn("metrics", snapshot)

    def test_generate_report(self) -> None:
        reporter = AutoReporterCentral(output_dir=self.tmp)
        result = reporter.generate()

        self.assertTrue(result["ok"])
        self.assertTrue((self.tmp / "k_atlas_central_report.json").exists())
        self.assertTrue((self.tmp / "k_atlas_central_report.md").exists())

        loaded = json.loads((self.tmp / "k_atlas_central_report.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "37")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/18_K_Atlas_AutoReporter_Central.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
