from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.blackboard.blackboard_agent import BlackboardAgent
from k_atlas.core.blackboard.blackboard_store import BlackboardStore
from k_atlas.core.blackboard.command_policy import evaluate_command
from k_atlas.core.blackboard.powershell_runner import PowerShellCommandRunner


class BlackboardSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_blackboard_"))
        self.store = BlackboardStore(
            messages_path=self.tmp / "messages.json",
            commands_path=self.tmp / "commands.json",
            results_path=self.tmp / "results.json",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_policy_allows_safe_git_status(self) -> None:
        result = evaluate_command("git status --short")
        self.assertTrue(result.ok)

    def test_policy_blocks_destructive_command(self) -> None:
        result = evaluate_command("Remove-Item -Recurse C:\\")
        self.assertFalse(result.ok)

    def test_agent_creates_safe_plan(self) -> None:
        agent = BlackboardAgent(self.store)
        result = agent.create_safe_plan("continuar K-Atlas")

        self.assertEqual(len(result["commands"]), 3)
        self.assertEqual(len(self.store.commands.load()), 3)

    def test_runner_executes_approved_safe_command_once(self) -> None:
        command = self.store.queue_command(
            title="Teste Write Host",
            command="Write-Host blackboard_ok",
            requested_by="smoke_test",
        )
        self.store.approve_command(command["command_id"], reviewer="test")

        runner = PowerShellCommandRunner(
            store=self.store,
            project_root=".",
            timeout_seconds=30,
        )
        results = runner.run_once()

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["ok"])
        self.assertIn("blackboard_ok", results[0]["stdout"])

    def test_page_compiles(self) -> None:
        self.assertTrue(Path("pages/11_K_Atlas_Lousa_Operacional.py").exists())
        py_compile.compile("pages/11_K_Atlas_Lousa_Operacional.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)