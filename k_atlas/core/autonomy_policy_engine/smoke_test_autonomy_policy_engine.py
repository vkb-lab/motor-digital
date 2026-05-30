from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.autonomy_policy_engine.policy import AutonomyPolicyEngine, validate_autonomy_request


class AutonomyPolicyEngineSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_autonomy_policy_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_blocks_auto_execute(self) -> None:
        result = validate_autonomy_request({"mode": "recommend", "auto_execute": True})
        self.assertFalse(result["ok"])
        self.assertIn("auto_execute_blocked", result["reasons"])

    def test_evaluate(self) -> None:
        engine = AutonomyPolicyEngine(memory_dir=self.tmp / "memory", reports_dir=self.tmp / "reports")
        result = engine.evaluate({"mode": "plan", "risk_level": "low"})
        self.assertTrue(result["ok"])
        self.assertFalse(result["validation"]["real_execution_enabled"])
        self.assertTrue((self.tmp / "reports" / "latest_autonomy_policy_engine.json").exists())

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/94_K_Atlas_Autonomy_Policy_Engine.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
