"""Agent for campaign generation."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from k_atlas.campaign_engine import generate_campaign


class CampaignAgent(BaseAgent):
    name = "campaign"
    description = "Creates local campaign plans"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        campaign = generate_campaign(
            name=context.get("name", task or "K-OS Campaign"),
            objective=context.get("objective", task or "Operar campanha local"),
            audience=context.get("audience", "publico geral"),
        )
        return {"agent": self.name, "status": "ok", "campaign": campaign}

