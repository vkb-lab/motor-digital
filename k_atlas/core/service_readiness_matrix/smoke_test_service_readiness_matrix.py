from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.service_readiness_matrix.matrix import ServiceReadinessMatrix
from k_atlas.core.service_readiness_matrix.policy import validate_service_readiness_payload


class ServiceReadinessMatrixSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_service_matrix_"))

        sample_reports = {
            "memory/local_daemon/heartbeat.json": {"status": "running"},
            "reports/command_center/latest_command_center_run.json": {"status": "completed"},
            "reports/mission_planner/latest_mission_plan.json": {"status": "planned"},
            "reports/daily_operator/latest_daily_operator_cockpit.json": {"status": "operational"},
            "reports/external_api_adapter/latest_external_api_adapter_readiness.json": {"status": "readiness_generated"},
            "reports/ai_provider_router/latest_ai_provider_router.json": {"status": "route_planned", "live_call_enabled": False},
            "reports/instagram_graph_readiness/latest_instagram_graph_readiness.json": {"status": "missing_credentials", "summary": {"publishing_enabled": False}},
            "reports/whatsapp_cloud_readiness/latest_whatsapp_cloud_readiness.json": {"status": "missing_credentials", "summary": {"message_send_enabled": False}},
            "reports/publish_approval_gate/latest_publish_approval_gate.json": {"status": "operational", "execution_enabled": False},
            "reports/external_action_stub/latest_external_action_stub.json": {"status": "completed", "real_execution_enabled": False},
            "reports/live_adapter_contract_registry/latest_live_adapter_contract_registry.json": {"status": "registered", "summary": {"live_execution_enabled": False}},
            "reports/adapter_dry_run_orchestrator/latest_adapter_dry_run_orchestrator.json": {"status": "dry_run_completed", "summary": {"real_execution_enabled": False}},
        }

        for relative_path, data in sample_reports.items():
            path = self.tmp / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_live_call(self) -> None:
        result = validate_service_readiness_payload({
            "scope": "all",
            "live_call": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("live_call_blocked", result["reasons"])

    def test_generate_matrix(self) -> None:
        matrix = ServiceReadinessMatrix(
            base_dir=self.tmp,
            reports_dir="reports/service_readiness_matrix",
            memory_dir="memory/service_readiness_matrix",
        )

        result = matrix.generate()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "58")
        self.assertGreaterEqual(result["summary"]["services_total"], 10)
        self.assertFalse(any(row["unsafe_flags"] for row in result["services"]))
        self.assertTrue((self.tmp / "reports/service_readiness_matrix/latest_service_readiness_matrix.json").exists())

        loaded = json.loads((self.tmp / "reports/service_readiness_matrix/latest_service_readiness_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "58")

    def test_scope_social(self) -> None:
        matrix = ServiceReadinessMatrix(
            base_dir=self.tmp,
            reports_dir="reports/service_readiness_matrix",
            memory_dir="memory/service_readiness_matrix",
        )

        result = matrix.generate({"scope": "social"})
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["summary"]["services_total"], 2)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/39_K_Atlas_Service_Readiness_Matrix.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
