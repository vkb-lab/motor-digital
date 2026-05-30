from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.lan_cockpit_access.lan import LANCockpitAccess
from k_atlas.core.lan_cockpit_access.policy import validate_lan_access_request


class LANCockpitAccessSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_lan_access_"))
        self.lan = LANCockpitAccess(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_public(self) -> None:
        result = validate_lan_access_request({"mode": "readiness", "public_exposure": True})
        self.assertFalse(result["ok"])

    def test_plan(self) -> None:
        result = self.lan.build_plan({"mode": "readiness", "port": 8506})
        self.assertEqual(result["checkpoint"], "81")
        self.assertFalse(result["server_started"])
        self.assertFalse(result["firewall_changed"])

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/81_K_Atlas_LAN_Cockpit_Access.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
