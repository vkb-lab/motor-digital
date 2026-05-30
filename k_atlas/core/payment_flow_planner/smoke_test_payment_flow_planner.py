from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.payment_flow_planner.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "394")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/394_K_Atlas_PaymentFlowPlanner.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
