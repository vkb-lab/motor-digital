from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.external_live_rollback_plan.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "272")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/272_K_Atlas_ExternalLiveRollbackPlan.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
