"""Agent registry for local operational agents."""

from __future__ import annotations

from typing import Any, Protocol


class AgentProtocol(Protocol):
    name: str

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ...


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentProtocol] = {}

    def register(self, agent: AgentProtocol) -> AgentProtocol:
        self._agents[agent.name] = agent
        return agent

    def get(self, name: str) -> AgentProtocol:
        if name not in self._agents:
            raise KeyError(f"Agent not registered: {name}")
        return self._agents[name]

    def names(self) -> list[str]:
        return sorted(self._agents)

    def all(self) -> dict[str, AgentProtocol]:
        return dict(self._agents)


registry = AgentRegistry()


def register_default_agents() -> AgentRegistry:
    from agents.campaign_agent import CampaignAgent
    from agents.memory_agent import MemoryAgent
    from agents.report_agent import ReportAgent
    from agents.system_agent import SystemAgent

    registry.register(SystemAgent())
    registry.register(MemoryAgent())
    registry.register(CampaignAgent())
    registry.register(ReportAgent())
    return registry

