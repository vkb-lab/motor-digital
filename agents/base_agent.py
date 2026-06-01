"""Base class for local K-OS agents."""

from __future__ import annotations

from typing import Any


class BaseAgent:
    name = "base"
    description = "Base operational agent"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "ok",
            "task": task,
            "context": context or {},
            "message": "Task handled by base agent",
        }

