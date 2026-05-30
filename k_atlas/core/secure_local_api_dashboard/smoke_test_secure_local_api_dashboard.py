from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.secure_local_api_dashboard.dashboard import SecureLocalApiDashboard


class SecureLocalApiDashboardSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_secure_api_dashboard_"))
        for path in [
            "k_atlas/core/secure_local_api_runtime",
            "k_atlas/core/local_api_auth_policy",
            "k_atlas/core/local_api_approval_bridge",
            "k_atlas/core/local_api_audit_ledger",
            "k_atlas/core/secure_local_api_dashboard",
        ]:
            (self.tmp / path).mkdir(parents=True, exist_ok=True)
        self.dashboard = SecureLocalApiDashboard(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_report(self) -> None:
        report = self.dashboard.build_report()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "93")
        self.assertEqual(report["summary"]["modules_ready"], 5)
        self.assertFalse(report["summary"]["remote_control_allowed"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/93_K_Atlas_Secure_Local_API_Dashboard.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
