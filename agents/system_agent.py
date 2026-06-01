"""Agent for local system status checks."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from k_atlas.paths import REQUIRED_DIRS, ensure_dirs


class SystemAgent(BaseAgent):
    name = "system"
    description = "Checks local K-OS system status"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ensure_dirs()
        return {
            "agent": self.name,
            "status": "ok",
            "task": task,
            "directories": {str(path): path.exists() for path in REQUIRED_DIRS},
        }

