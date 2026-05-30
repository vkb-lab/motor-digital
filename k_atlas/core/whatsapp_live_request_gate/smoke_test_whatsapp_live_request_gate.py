from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.whatsapp_live_request_gate.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "260")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/260_K_Atlas_WhatsappLiveRequestGate.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
