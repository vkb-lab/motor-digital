from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_action_contracts.contracts import LocalActionContractRegistry, validate_action_request
from k_atlas.core.local_action_router.router import LocalActionRouter
from k_atlas.core.local_execution_queue.queue import LocalExecutionQueue
from k_atlas.core.local_action_audit_ledger.ledger import LocalActionAuditLedger
from k_atlas.core.assisted_execution_dashboard.dashboard import AssistedExecutionDashboard


class AssistedExecutionLayerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_assisted_exec_"))
        self.cwd = Path.cwd()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_contract_policy_blocks_auto_execute(self) -> None:
        result = validate_action_request({
            "action_type": "run_mission_pipeline",
            "human_approved": True,
            "auto_execute": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_full_assisted_execution_layer(self) -> None:
        registry = LocalActionContractRegistry(
            live_dir=self.tmp / "live" / "contracts",
            reports_dir=self.tmp / "reports" / "contracts",
            memory_dir=self.tmp / "memory" / "contracts",
        )
        registry.build_contracts()

        router = LocalActionRouter(
            live_dir=self.tmp / "live" / "router",
            reports_dir=self.tmp / "reports" / "router",
            memory_dir=self.tmp / "memory" / "router",
        )
        route = router.route({
            "action_type": "run_mission_pipeline",
            "human_approved": True,
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
            "remote_control_enabled": False,
        })

        self.assertTrue(route["ok"])
        self.assertEqual(route["status"], "route_ready")

        queue = LocalExecutionQueue(
            route_queue_path=self.tmp / "live" / "router" / "action_route_queue.json",
            live_dir=self.tmp / "live" / "queue",
            reports_dir=self.tmp / "reports" / "queue",
            memory_dir=self.tmp / "memory" / "queue",
        )
        queued = queue.enqueue_latest_ready_route()
        self.assertTrue(queued["ok"])
        self.assertEqual(queued["status"], "execution_item_queued")

        ledger = LocalActionAuditLedger(
            route_queue_path=self.tmp / "live" / "router" / "action_route_queue.json",
            execution_queue_path=self.tmp / "live" / "queue" / "execution_queue.json",
            memory_dir=self.tmp / "memory" / "ledger",
            reports_dir=self.tmp / "reports" / "ledger",
        )
        ledger_report = ledger.build_report()
        self.assertTrue(ledger_report["ok"])
        self.assertEqual(ledger_report["summary"]["executions_total"], 1)

    def test_dashboard_report(self) -> None:
        report = AssistedExecutionDashboard(reports_dir=self.tmp / "reports" / "dashboard").build_report()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "88")
        self.assertFalse(report["summary"]["real_execution_enabled"])

    def test_pages_compile(self) -> None:
        for page in [
            "pages/84_K_Atlas_Local_Action_Contracts.py",
            "pages/85_K_Atlas_Local_Action_Router.py",
            "pages/86_K_Atlas_Local_Execution_Queue.py",
            "pages/87_K_Atlas_Local_Action_Audit_Ledger.py",
            "pages/88_K_Atlas_Assisted_Execution_Dashboard.py",
        ]:
            py_compile.compile(page, doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
