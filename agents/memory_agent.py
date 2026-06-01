"""Agent for operational memory tasks."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from k_atlas.memory_store import MemoryStore


class MemoryAgent(BaseAgent):
    name = "memory"
    description = "Records and retrieves operational memory"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        store = MemoryStore()
        item = store.add("agent_task", {"task": task, "context": context or {}}, ["agent", "memory"])
        return {"agent": self.name, "status": "ok", "stored": item, "total_items": len(store.all())}

