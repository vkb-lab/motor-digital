from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autonomy_audit_monitor.monitor import AutonomyAuditMonitor


class AutonomyAuditMonitorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_autonomy_audit_"))
        self.queue = self.tmp / "queue.json"
        self.queue.write_text(json.dumps([
            {
                "queue_id": "q1",
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
            }
        ]), encoding="utf-8")
        self.monitor = AutonomyAuditMonitor(
            supervised_queue_path=self.queue,
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_audit_clean(self) -> None:
        result = self.monitor.audit()
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["violations_total"], 0)

    def test_audit_detects_violation(self) -> None:
        self.queue.write_text(json.dumps([{"queue_id": "q2", "real_execution_enabled": True}]), encoding="utf-8")
        result = self.monitor.audit()
        self.assertFalse(result["ok"])
        self.assertEqual(result["summary"]["violations_total"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/97_K_Atlas_Autonomy_Audit_Monitor.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
