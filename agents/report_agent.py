"""Agent for report generation."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from k_atlas.reporting import generate_report


class ReportAgent(BaseAgent):
    name = "report"
    description = "Generates markdown operational reports"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        path = generate_report(task or "K-OS Agent Report", context or {})
        return {"agent": self.name, "status": "ok", "report_path": str(path)}

