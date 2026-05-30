from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.remote_tunnel_gate.gate import RemoteTunnelGate
from k_atlas.core.remote_tunnel_gate.policy import validate_tunnel_request


class RemoteTunnelGateSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_tunnel_gate_"))
        self.gate = RemoteTunnelGate(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_start_tunnel(self) -> None:
        result = validate_tunnel_request({"provider": "manual", "start_tunnel": True})
        self.assertFalse(result["ok"])
        self.assertIn("start_tunnel_blocked", result["reasons"])

    def test_create_request(self) -> None:
        item = self.gate.create_request({"provider": "manual", "start_tunnel": False})
        self.assertEqual(item["status"], "waiting_human_remote_review")
        self.assertFalse(item["tunnel_started"])
        self.assertTrue((self.tmp / "live" / "remote_tunnel_gate" / "tunnel_gate_queue.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/82_K_Atlas_Remote_Tunnel_Gate.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
