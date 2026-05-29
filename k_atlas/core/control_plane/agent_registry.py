from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentDefinition:
    agent_id: str
    name: str
    role: str
    domain: str
    autonomy_level: int
    allowed_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    requires_supervision: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}

    def register(self, agent: AgentDefinition) -> None:
        if not agent.agent_id:
            raise ValueError("agent_id obrigatorio")
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> AgentDefinition:
        if agent_id not in self._agents:
            raise KeyError(f"Agente nao registrado: {agent_id}")
        return self._agents[agent_id]

    def list_agents(self) -> list[AgentDefinition]:
        return [self._agents[key] for key in sorted(self._agents)]

    def to_dict(self) -> dict[str, Any]:
        return {agent.agent_id: agent.to_dict() for agent in self.list_agents()}


def build_default_agent_registry() -> AgentRegistry:
    registry = AgentRegistry()

    registry.register(AgentDefinition(
        agent_id="k_social_operator",
        name="K-Social Operator",
        role="Operador de midias digitais e campanhas",
        domain="social",
        autonomy_level=2,
        allowed_actions=[
            "create_campaign",
            "create_content_package",
            "enqueue_publish_payload",
            "dry_run",
            "test_page_publish",
        ],
        blocked_actions=[
            "official_publish",
            "mass_messaging",
            "browser_automation",
            "plaintext_secret",
        ],
        requires_supervision=True,
    ))

    registry.register(AgentDefinition(
        agent_id="k_saas_builder",
        name="K-SaaS Builder",
        role="Construtor de MVPs, produtos digitais e apps",
        domain="saas_factory",
        autonomy_level=2,
        allowed_actions=[
            "create_product_structure",
            "generate_app_module",
            "run_smoke_test",
            "prepare_deploy",
        ],
        blocked_actions=[
            "delete_production_data",
            "deploy_without_test",
            "store_secret_plaintext",
        ],
        requires_supervision=True,
    ))

    registry.register(AgentDefinition(
        agent_id="k_creative_director",
        name="K-Creative Director",
        role="Diretor criativo audiovisual e visual",
        domain="creative",
        autonomy_level=2,
        allowed_actions=[
            "create_brief",
            "create_prompt_pack",
            "generate_asset_plan",
            "prepare_media_package",
        ],
        blocked_actions=[
            "external_api_without_vault",
            "use_unlicensed_asset",
        ],
        requires_supervision=True,
    ))

    registry.register(AgentDefinition(
        agent_id="k_autoreporter",
        name="K-AutoReporter",
        role="Gerador de relatorios operacionais",
        domain="reports",
        autonomy_level=3,
        allowed_actions=[
            "read_events",
            "summarize_state",
            "generate_report",
        ],
        blocked_actions=[
            "publish_external",
            "modify_credentials",
        ],
        requires_supervision=False,
    ))

    registry.register(AgentDefinition(
        agent_id="k_supervisor",
        name="K-Supervisor",
        role="Supervisor humano assistido",
        domain="governance",
        autonomy_level=5,
        allowed_actions=[
            "approve",
            "reject",
            "request_revision",
            "authorize_sandbox",
        ],
        blocked_actions=[
            "bypass_audit",
            "plaintext_secret",
        ],
        requires_supervision=False,
    ))

    return registry