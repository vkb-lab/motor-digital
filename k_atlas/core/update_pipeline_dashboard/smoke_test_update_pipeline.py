from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.update_intake_queue.queue import UpdateIntakeQueue
from k_atlas.core.update_verification_gate.gate import UpdateVerificationGate
from k_atlas.core.update_apply_runner.runner import UpdateApplyRunner
from k_atlas.core.update_rollback_hook.hook import UpdateRollbackHook
from k_atlas.core.update_pipeline_dashboard.dashboard import UpdatePipelineDashboard


class UpdatePipelineSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_update_pipeline_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_update_pipeline(self) -> None:
        intake = UpdateIntakeQueue(
            live_dir=self.tmp / "live" / "update_intake_queue",
            memory_dir=self.tmp / "memory" / "update_intake_queue",
            reports_dir=self.tmp / "reports" / "update_intake_queue",
        )
        item = intake.enqueue({"installer_name": "K_ATLAS_TEST.ps1"})
        self.assertEqual(item["status"], "queued_for_verification")

        gate = UpdateVerificationGate(
            queue_path=self.tmp / "live" / "update_intake_queue" / "update_queue.json",
            live_dir=self.tmp / "live" / "update_verification_gate",
            reports_dir=self.tmp / "reports" / "update_verification_gate",
        )
        gate_report = gate.build_verified_queue()
        self.assertEqual(gate_report["summary"]["ready_for_supervised_apply"], 1)

        runner = UpdateApplyRunner(
            verified_path=self.tmp / "live" / "update_verification_gate" / "verified_updates.json",
            memory_dir=self.tmp / "memory" / "update_apply_runner",
            reports_dir=self.tmp / "reports" / "update_apply_runner",
        )
        dry = runner.dry_run()
        self.assertEqual(dry["summary"]["ready_updates"], 1)
        record = runner.record_supervised_apply_ready()
        self.assertEqual(record["status"], "supervised_apply_ready")

        hook = UpdateRollbackHook(
            memory_dir=self.tmp / "memory" / "update_rollback_hook",
            reports_dir=self.tmp / "reports" / "update_rollback_hook",
        )
        hook_report = hook.create_hook()
        self.assertTrue(hook_report["latest_hook"]["rollback_available"])

    def test_dashboard_report(self) -> None:
        dashboard = UpdatePipelineDashboard(reports_dir=self.tmp / "reports" / "update_pipeline_dashboard")
        report = dashboard.build_report()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "117")

    def test_pages_compile(self) -> None:
        pages = [
            "pages/113_K_Atlas_Update_Intake_Queue.py",
            "pages/114_K_Atlas_Update_Verification_Gate.py",
            "pages/115_K_Atlas_Update_Apply_Runner.py",
            "pages/116_K_Atlas_Update_Rollback_Hook.py",
            "pages/117_K_Atlas_Update_Pipeline_Dashboard.py",
        ]
        for page in pages:
            py_compile.compile(page, doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
