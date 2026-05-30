from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autoprogramming_cycle_dashboard.dashboard import AutoprogrammingCycleDashboard


class AutoprogrammingCycleDashboardSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_cycle_dashboard_"))

        required_dirs = [
            "k_atlas/core/assisted_autoprogramming",
            "k_atlas/core/autoprogramming_proposal_reviewer",
            "k_atlas/core/autoprogramming_apply_package_builder",
            "k_atlas/core/autoprogramming_apply_package_gate",
            "k_atlas/core/manual_apply_executor",
            "k_atlas/core/manual_apply_rollback_executor",
        ]

        for item in required_dirs:
            (self.tmp / item).mkdir(parents=True, exist_ok=True)

        required_files = [
            "pages/68_K_Atlas_Autoprogramming_Apply_Package_Gate.py",
            "pages/69_K_Atlas_Manual_Apply_Executor.py",
            "pages/70_K_Atlas_Manual_Apply_Rollback_Executor.py",
            "README_AUTOPROGRAMMING_APPLY_PACKAGE_GATE.md",
            "README_MANUAL_APPLY_EXECUTOR.md",
            "README_MANUAL_APPLY_ROLLBACK_EXECUTOR.md",
            "reports/cowork_pilot_studio/milestone_cycle_65_70.md",
            "reports/cowork_pilot_studio/cowork_session_65_70_index.md",
            "reports/cowork_pilot_studio/latest_recording.json",
        ]

        for item in required_files:
            target = self.tmp / item
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("demo", encoding="utf-8")

        queues = {
            "live/autoprogramming_proposal_reviewer/review_queue.json": [{"id": 1}],
            "live/autoprogramming_apply_package_builder/apply_package_queue.json": [{"id": 1}],
            "live/autoprogramming_apply_package_gate/apply_package_gate_queue.json": [{"id": 1}],
            "memory/manual_apply_executor/apply_manifest.json": [{"id": 1}],
            "memory/manual_apply_rollback_executor/rollback_manifest.json": [{"id": 1}],
        }

        for path, data in queues.items():
            target = self.tmp / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data), encoding="utf-8")

        self.dashboard = AutoprogrammingCycleDashboard(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_report(self) -> None:
        report = self.dashboard.build_report()

        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "71")
        self.assertEqual(report["summary"]["checkpoints_total"], 6)
        self.assertEqual(report["summary"]["checkpoints_operational"], 6)
        self.assertTrue(report["summary"]["cycle_ready"])
        self.assertEqual(report["queues"]["manual_apply_manifest"], 1)

    def test_report_files_created(self) -> None:
        self.dashboard.build_report()

        self.assertTrue((self.tmp / "reports" / "autoprogramming_cycle_dashboard" / "latest_autoprogramming_cycle_dashboard.json").exists())
        self.assertTrue((self.tmp / "reports" / "autoprogramming_cycle_dashboard" / "latest_autoprogramming_cycle_dashboard.md").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/71_K_Atlas_Autoprogramming_Cycle_Dashboard.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
