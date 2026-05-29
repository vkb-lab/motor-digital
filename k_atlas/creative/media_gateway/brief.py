from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CreativeBrief:
    project_name: str
    objective: str
    target_audience: str
    offer: str
    channel: str
    tone: str
    visual_style: str
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_default_k_atlas_brief() -> CreativeBrief:
    return CreativeBrief(
        project_name="K-Atlas OS",
        objective="Apresentar o K-Atlas como sistema operacional de agentes IA para criar SaaS, campanhas, automações e produtos digitais com supervisão humana.",
        target_audience="empreendedores, criadores de produtos digitais, operadores de marketing, builders, founders e empresas que querem escalar com IA operacional.",
        offer="acompanhar a construção pública de um ecossistema IA capaz de criar produtos, campanhas e sistemas com governança.",
        channel="instagram_official",
        tone="arrojado, técnico, direto, ambicioso e orientado à execução real.",
        visual_style="futurista limpo, cockpit operacional, prints reais, diagramas simples, preto, branco, cinza, azul e vermelho pontual.",
        constraints=[
            "sem publicação automática",
            "sem promessa falsa",
            "sem token em texto puro",
            "sem API externa sem Credential Vault",
            "sem uso de ativos sem licença",
            "todo pacote precisa de aprovação humana",
        ],
    )


def build_custom_brief(
    project_name: str,
    objective: str,
    target_audience: str,
    offer: str,
    channel: str = "generic",
    tone: str = "direto, técnico e comercial",
    visual_style: str = "moderno, limpo e de alta conversão",
    constraints: list[str] | None = None,
) -> CreativeBrief:
    return CreativeBrief(
        project_name=project_name.strip() or "Projeto K-Atlas",
        objective=objective.strip() or "Criar pacote criativo supervisionado.",
        target_audience=target_audience.strip() or "público qualificado",
        offer=offer.strip() or "proposta de valor clara",
        channel=channel.strip() or "generic",
        tone=tone.strip() or "direto",
        visual_style=visual_style.strip() or "moderno",
        constraints=constraints or [
            "human_review_required",
            "external_api_disabled_by_default",
        ],
    )