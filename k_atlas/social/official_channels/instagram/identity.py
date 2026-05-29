from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class InstagramIdentity:
    handle_options: list[str]
    display_name: str
    positioning: str
    bio_options: list[str]
    content_pillars: list[str]
    visual_direction: list[str]
    tone_of_voice: list[str]
    prohibited_actions: list[str]
    approval_rules: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_k_atlas_instagram_identity() -> InstagramIdentity:
    return InstagramIdentity(
        handle_options=[
            "katlas.os",
            "k.atlas.os",
            "katlas.ai",
            "katlas.engine",
        ],
        display_name="K-Atlas OS",
        positioning=(
            "Sistema operacional de agentes IA para criar, operar e escalar produtos digitais, "
            "campanhas, SaaS, automações e inteligência comercial com supervisão humana."
        ),
        bio_options=[
            "Sistema operacional de agentes IA. Criamos SaaS, campanhas e automações com supervisão humana.",
            "AI Operating System para produtos digitais, campanhas e automações. Construindo unicórnios que geram unicórnios.",
            "K-Atlas OS: agentes IA, SaaS Factory, campanhas, automações e cockpit operacional.",
        ],
        content_pillars=[
            "Construção pública do K-Atlas OS",
            "Agentes IA em operação real",
            "SaaS Factory e produtos digitais",
            "Marketing inteligente e automações",
            "Bastidores técnicos e evolução supervisionada",
            "Cases, protótipos e validações",
            "Manifesto: unicórnio gerador de unicórnios",
        ],
        visual_direction=[
            "visual futurista limpo",
            "cockpit operacional",
            "prints reais do sistema",
            "diagramas de arquitetura simples",
            "vídeos curtos mostrando execução",
            "antes/depois de automações",
            "identidade preta, branca, azul, cinza e vermelho pontual",
        ],
        tone_of_voice=[
            "arrojado",
            "técnico",
            "direto",
            "growth-minded",
            "ambicioso",
            "sem hype vazio",
            "execução real acima de promessa",
        ],
        prohibited_actions=[
            "publicar sem aprovação humana",
            "enviar DM automática",
            "seguir/deixar de seguir automaticamente",
            "curtir/comentar automaticamente",
            "usar token em texto puro",
            "usar automação de navegador para operação oficial",
            "usar API externa sem Credential Vault",
        ],
        approval_rules=[
            "todo post oficial precisa de aprovação humana",
            "todo criativo precisa passar por audit log",
            "toda API oficial precisa usar vault",
            "toda publicação deve ser reversível ou rastreável",
            "nenhuma mensagem em massa sem consentimento explícito",
        ],
    )