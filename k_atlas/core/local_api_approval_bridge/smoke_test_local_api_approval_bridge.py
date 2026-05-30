from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_api_approval_bridge.bridge import LocalApiApprovalBridge


class LocalApiApprovalBridgeSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_api_bridge_"))
        self.bridge = LocalApiApprovalBridge(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_request(self) -> None:
        item = self.bridge.create_request({"source": "test", "intent": "queue"})
        self.assertEqual(item["status"], "waiting_human_approval")
        self.assertFalse(item["real_execution_enabled"])
        self.assertTrue((self.tmp / "live" / "local_api_approval_bridge" / "api_approval_queue.json").exists())

    def test_summary(self) -> None:
        self.bridge.create_request({"source": "test"})
        summary = self.bridge.summary()
        self.assertEqual(summary["summary"]["approval_queue_total"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/91_K_Atlas_API_Approval_Bridge.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
