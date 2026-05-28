# -*- coding: utf-8 -*-
"""
Smoke test do OrchestratorAgent.

Uso:
python smoke_test_orchestrator_agent.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from agents.memory_agent import MemoryAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.system_agent import SystemAgent
from agents.task_agent import TaskAgent
from core.kernel import create_kernel


ROOT = Path(__file__).resolve().parent


def assert_success(result, label: str) -> None:
    if not result.success:
        print(label)
        print(result.to_dict())
        raise SystemExit(1)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        kernel = create_kernel(root_path=ROOT)
        kernel.start(load_state=True)

        system_agent = SystemAgent(kernel=kernel)
        kernel.register_agent(system_agent, replace=True, roles=["system"])

        task_agent = TaskAgent(storage_path=temp_path / "tasks_test.json")
        kernel.register_agent(task_agent, replace=True, roles=["agent"])

        memory_agent = MemoryAgent(storage_path=temp_path / "entries_test.json")
        kernel.register_agent(memory_agent, replace=True, roles=["agent"])

        orchestrator_agent = OrchestratorAgent(kernel=kernel)
        kernel.register_agent(orchestrator_agent, replace=True, roles=["system"])

        ping = kernel.execute("orchestrator_agent.ping")
        assert_success(ping, "ping failed")

        status = kernel.execute("orchestrator_agent.status")
        assert_success(status, "status failed")

        plan = kernel.execute(
            "orchestrator_agent.plan",
            payload={
                "goal": "Validar coordenacao multiagente inicial",
                "description": "Teste automatico do OrchestratorAgent.",
                "priority": "high",
                "tags": ["smoke_test", "orchestrator"],
                "assigned_agent_id": "task_agent",
            },
        )
        assert_success(plan, "plan failed")

        handoff = kernel.execute(
            "orchestrator_agent.handoff",
            payload={
                "target_agent_id": "task_agent",
                "title": "Executar handoff de teste",
                "description": "Handoff criado pelo smoke test.",
                "priority": "normal",
                "tags": ["smoke_test"],
            },
        )
        assert_success(handoff, "handoff failed")

        daily = kernel.execute(
            "orchestrator_agent.daily_start",
            payload={
                "focus": "Validar inicio operacional diario do K-Atlas OS.",
                "priority": "normal",
                "tags": ["smoke_test", "daily"],
            },
        )
        assert_success(daily, "daily_start failed")

        print("OrchestratorAgent smoke test OK")

        kernel.stop(save_state=True)
