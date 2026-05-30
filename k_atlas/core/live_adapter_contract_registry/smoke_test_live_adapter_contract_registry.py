from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.live_adapter_contract_registry.policy import validate_live_adapter_contract
from k_atlas.core.live_adapter_contract_registry.registry import LiveAdapterContractRegistry


class LiveAdapterContractRegistrySmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_live_adapter_registry_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_blocks_enabled_adapter(self) -> None:
        result = validate_live_adapter_contract({
            "adapter_id": "instagram_graph_publish",
            "risk_level": "critical",
            "env_vars": ["META_ACCESS_TOKEN"],
            "enabled": True,
            "requires_human_approval": True,
            "requires_approval_gate": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("enabled_blocked", result["reasons"])

    def test_policy_blocks_token_value(self) -> None:
        result = validate_live_adapter_contract({
            "adapter_id": "openai_live",
            "risk_level": "medium",
            "env_vars": ["OPENAI_API_KEY=abc"],
            "requires_human_approval": True,
            "requires_approval_gate": True,
        })
        self.assertFalse(result["ok"])
        self.assertIn("env_var_must_not_contain_value", result["reasons"])

    def test_register_contracts(self) -> None:
        registry = LiveAdapterContractRegistry(
            reports_dir=self.tmp / "reports",
            memory_dir=self.tmp / "memory",
        )

        result = registry.register_contracts()

        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "56")
        self.assertFalse(result["summary"]["live_execution_enabled"])
        self.assertGreaterEqual(result["summary"]["contracts_total"], 5)
        self.assertTrue((self.tmp / "reports" / "latest_live_adapter_contract_registry.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_live_adapter_contract_registry.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "56")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/37_K_Atlas_Live_Adapter_Contract_Registry.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
