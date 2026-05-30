from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.adapter_dry_run_orchestrator.orchestrator import AdapterDryRunOrchestrator
from k_atlas.core.adapter_dry_run_orchestrator.policy import validate_adapter_dry_run_payload
from k_atlas.core.live_adapter_contract_registry.registry import LiveAdapterContractRegistry


class AdapterDryRunOrchestratorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_adapter_dry_run_"))
        self.registry = LiveAdapterContractRegistry(
            reports_dir=self.tmp / "registry_reports",
            memory_dir=self.tmp / "registry_memory",
        )
        self.registry.register_contracts()

        self.orchestrator = AdapterDryRunOrchestrator(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
            registry=self.registry,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_live_call(self) -> None:
        result = validate_adapter_dry_run_payload({
            "scope": "all",
            "live_call": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("live_call_blocked", result["reasons"])

    def test_run_all(self) -> None:
        result = self.orchestrator.run()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "57")
        self.assertGreaterEqual(result["summary"]["contracts_checked"], 5)
        self.assertFalse(result["summary"]["execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_adapter_dry_run_orchestrator.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_adapter_dry_run_orchestrator.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "57")

    def test_run_scope_instagram(self) -> None:
        result = self.orchestrator.run({"scope": "instagram"})
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["summary"]["contracts_checked"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/38_K_Atlas_Adapter_Dry_Run_Orchestrator.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
