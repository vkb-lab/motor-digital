"""Task execution wrapper around registered agents."""

from __future__ import annotations

from typing import Any

from .agent_registry import AgentRegistry, register_default_agents
from .events import emit_event


class TaskRunner:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or register_default_agents()

    def run(self, agent_name: str, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        emit_event("task_started", {"agent": agent_name, "task": task})
        agent = self.registry.get(agent_name)
        result = agent.run(task, context or {})
        emit_event("task_finished", {"agent": agent_name, "task": task, "status": result.get("status", "unknown")})
        return result

