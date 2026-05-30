from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.saas_metrics_collector.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "354")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/354_K_Atlas_SaasMetricsCollector.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
