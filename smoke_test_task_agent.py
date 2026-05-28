# -*- coding: utf-8 -*-
"""
Smoke test do TaskAgent.

Uso:
python smoke_test_task_agent.py
"""

from __future__ import annotations

from pathlib import Path

from agents.task_agent import TaskAgent
from core.kernel import create_kernel


ROOT = Path(__file__).resolve().parent


def assert_success(result, label: str) -> None:
    if not result.success:
        print(label)
        print(result.to_dict())
        raise SystemExit(1)


if __name__ == "__main__":
    kernel = create_kernel(root_path=ROOT)
    kernel.start(load_state=True)

    task_agent = TaskAgent(storage_path=ROOT / "memory" / "tasks.json")
    kernel.register_agent(task_agent, replace=True, roles=["agent"])

    ping = kernel.execute("task_agent.ping")
    assert_success(ping, "ping failed")

    created = kernel.execute(
        "task_agent.create",
        payload={
            "title": "Validar TaskAgent",
            "description": "Teste automatico do agente de tarefas.",
            "priority": "high",
            "tags": ["smoke_test", "task_agent"],
            "assigned_agent_id": "task_agent",
        },
    )
    assert_success(created, "create failed")

    task_id = created.output["task"]["task_id"]

    listed = kernel.execute("task_agent.list", payload={"limit": 10})
    assert_success(listed, "list failed")

    loaded = kernel.execute("task_agent.get", payload={"task_id": task_id})
    assert_success(loaded, "get failed")

    completed = kernel.execute("task_agent.complete", payload={"task_id": task_id})
    assert_success(completed, "complete failed")

    stats = kernel.execute("task_agent.stats")
    assert_success(stats, "stats failed")

    print("TaskAgent smoke test OK")
    print("task_id:", task_id)
    print("total_tasks:", stats.output["total"])

    kernel.stop(save_state=True)
