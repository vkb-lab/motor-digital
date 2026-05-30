from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.saas_board_review_gate.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "366")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/366_K_Atlas_SaasBoardReviewGate.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
