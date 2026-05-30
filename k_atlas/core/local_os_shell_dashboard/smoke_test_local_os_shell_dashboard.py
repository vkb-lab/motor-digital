from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_os_shell_dashboard.shell import LocalOSShellDashboard


class LocalOSShellDashboardSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_local_os_shell_"))
        for path in [
            "k_atlas/core/local_control_plane",
            "k_atlas/core/remote_assist_readiness",
            "k_atlas/core/secure_local_api_readiness",
            "k_atlas/core/operator_approval_console",
            "k_atlas/core/lan_cockpit_access",
            "k_atlas/core/remote_tunnel_gate",
        ]:
            (self.tmp / path).mkdir(parents=True, exist_ok=True)
        self.shell = LocalOSShellDashboard(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_report(self) -> None:
        result = self.shell.build_report()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "83")
        self.assertTrue(result["summary"]["local_os_ready"])
        self.assertFalse(result["summary"]["remote_control_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/83_K_Atlas_Local_OS_Shell.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
