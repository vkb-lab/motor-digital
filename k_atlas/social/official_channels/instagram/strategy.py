from __future__ import annotations

from typing import Any

from .identity import build_k_atlas_instagram_identity


def build_instagram_launch_strategy() -> dict[str, Any]:
    identity = build_k_atlas_instagram_identity()

    return {
        "channel": "instagram",
        "status": "planning_only",
        "official_publish_allowed": False,
        "auto_publish_allowed": False,
        "identity": identity.to_dict(),
        "launch_sequence": [
            {
                "step": 1,
                "name": "definir handle final",
                "output": "handle aprovado manualmente",
            },
            {
                "step": 2,
                "name": "criar bio e foto de perfil",
                "output": "perfil pronto para aprovação",
            },
            {
                "step": 3,
                "name": "criar 9 posts base",
                "output": "grade inicial conceitual",
            },
            {
                "step": 4,
                "name": "criar 3 reels demonstrativos",
                "output": "vídeos curtos do sistema em operação",
            },
            {
                "step": 5,
                "name": "publicar manualmente ou via API oficial futura",
                "output": "publicação somente após vault + aprovação",
            },
        ],
        "first_9_posts": [
            "O que é o K-Atlas OS",
            "Por que agentes IA precisam de governança",
            "Control Plane em operação",
            "Lousa Operacional + PowerShell Runner",
            "SaaS Factory: criando produtos digitais",
            "K-Social: mídia digital supervisionada",
            "Creative Media Gateway: audiovisual para produtos",
            "Autonomy Ladder: níveis de independência",
            "Manifesto: unicórnio gerador de unicórnios",
        ],
        "first_3_reels": [
            {
                "title": "O K-Atlas executando comandos supervisionados",
                "format": "screen recording vertical 9:16",
                "hook": "Isso não é chatbot. É um sistema operacional de agentes IA.",
            },
            {
                "title": "Do objetivo ao executor",
                "format": "motion diagram + cockpit",
                "hook": "Um objetivo vira tarefa, aprovação, execução e log.",
            },
            {
                "title": "Construindo SaaS com agentes",
                "format": "screen recording + narração",
                "hook": "O próximo SaaS não nasce em uma reunião. Nasce em um cockpit.",
            },
        ],
    }