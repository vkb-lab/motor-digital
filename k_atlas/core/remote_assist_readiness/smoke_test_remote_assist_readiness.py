from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.remote_assist_readiness.policy import validate_remote_assist_request
from k_atlas.core.remote_assist_readiness.readiness import RemoteAssistReadiness


class RemoteAssistReadinessSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_remote_readiness_"))
        self.readiness = RemoteAssistReadiness(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_remote_control(self) -> None:
        result = validate_remote_assist_request({
            "mode": "lan_readiness",
            "network_scope": "lan_only",
            "remote_control_enabled": True,
        })

        self.assertFalse(result["ok"])
        self.assertIn("remote_control_enabled_blocked", result["reasons"])
        self.assertFalse(result["remote_control_allowed"])

    def test_policy_requires_approval_for_tunnel_proposal(self) -> None:
        result = validate_remote_assist_request({
            "mode": "tunnel_proposal",
            "network_scope": "tunnel_proposal_only",
            "human_approved": False,
        })

        self.assertFalse(result["ok"])
        self.assertIn("human_approval_required_for_tunnel_proposal", result["reasons"])

    def test_build_readiness_report(self) -> None:
        result = self.readiness.build_readiness({
            "mode": "lan_readiness",
            "network_scope": "lan_only",
            "human_approved": False,
            "public_exposure_enabled": False,
            "remote_control_enabled": False,
            "unattended_access_enabled": False,
            "mouse_automation": False,
            "keyboard_automation": False,
            "credential_capture_enabled": False,
            "password_storage_enabled": False,
            "auto_execute": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "external_api_enabled": False,
        })

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "78")
        self.assertFalse(result["summary"]["remote_control_enabled"])
        self.assertTrue((self.tmp / "reports" / "remote_assist_readiness" / "latest_remote_assist_readiness.json").exists())
        self.assertTrue((self.tmp / "live" / "remote_assist_readiness" / "readiness_state.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/78_K_Atlas_Remote_Assist_Readiness.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
