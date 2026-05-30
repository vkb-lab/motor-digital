from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.saas_deploy_dashboard.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "328")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/328_K_Atlas_SaasDeployDashboard.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
