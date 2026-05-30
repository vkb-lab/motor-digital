from __future__ import annotations
import json, py_compile, shutil, tempfile, unittest
from pathlib import Path
from k_atlas.core.autoprogramming_cycle_controller.controller import AutoprogrammingCycleController
from k_atlas.core.autoprogramming_cycle_controller.policy import validate_cycle_control_request

class Smoke(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="k_cycle_controller_"))
        for d in ["assisted_autoprogramming","autoprogramming_proposal_reviewer","autoprogramming_apply_package_builder","autoprogramming_apply_package_gate","manual_apply_executor","manual_apply_rollback_executor"]:
            (self.tmp / "k_atlas" / "core" / d).mkdir(parents=True, exist_ok=True)
        files = [
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
        for f in files:
            p = self.tmp / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("demo", encoding="utf-8")
        queues = {
            "live/autoprogramming_proposal_reviewer/review_queue.json": [{"id": 1}],
            "live/autoprogramming_apply_package_builder/apply_package_queue.json": [{"id": 1}],
            "live/autoprogramming_apply_package_gate/apply_package_gate_queue.json": [{"id": 1}],
            "memory/manual_apply_executor/apply_manifest.json": [{"id": 1}],
            "memory/manual_apply_rollback_executor/rollback_manifest.json": [{"id": 1}],
        }
        for path, data in queues.items():
            p = self.tmp / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data), encoding="utf-8")
        self.controller = AutoprogrammingCycleController(project_root=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_auto_execute(self):
        r = validate_cycle_control_request({"mode": "recommend", "auto_execute": True})
        self.assertFalse(r["ok"])
        self.assertIn("auto_execute_blocked", r["reasons"])

    def test_build_decision(self):
        d = self.controller.build_decision({"mode": "recommend"})
        self.assertTrue(d["ok"])
        self.assertEqual(d["checkpoint"], "72")
        self.assertEqual(d["status"], "decision_ready")
        self.assertFalse(d["automatic_execution_allowed"])
        self.assertTrue((self.tmp / "live/autoprogramming_cycle_controller/cycle_decision_queue.json").exists())

    def test_summary(self):
        self.controller.build_decision({"mode": "recommend"})
        s = self.controller.summary()
        self.assertEqual(s["summary"]["decision_queue_total"], 1)
        self.assertTrue(s["summary"]["cycle_ready"])

    def test_page_compiles(self):
        py_compile.compile("pages/72_K_Atlas_Autoprogramming_Cycle_Controller.py", doraise=True)

if __name__ == "__main__":
    unittest.main(verbosity=2)
