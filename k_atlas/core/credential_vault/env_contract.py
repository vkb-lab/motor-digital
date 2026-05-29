from __future__ import annotations

from typing import Any


def build_env_contract() -> dict[str, Any]:
    return {
        "checkpoint": "35",
        "module": "credential_vault",
        "status": "planning_and_validation",
        "required_now": [],
        "future_optional": [
            {
                "name": "META_GRAPH_ACCESS_TOKEN",
                "purpose": "Instagram/Meta API futura",
                "required_for": "level_4_official_publish",
                "storage": "Render environment variable",
            },
            {
                "name": "WHATSAPP_CLOUD_API_TOKEN",
                "purpose": "WhatsApp Cloud API futura",
                "required_for": "level_5_consent_messaging",
                "storage": "Render environment variable",
            },
            {
                "name": "GOOGLE_AI_API_KEY",
                "purpose": "Google audiovisual/image/video generation futura",
                "required_for": "creative_media_generation",
                "storage": "Render environment variable",
            },
            {
                "name": "OPENAI_API_KEY",
                "purpose": "OpenAI API futura",
                "required_for": "cloud_agents_optional",
                "storage": "Render environment variable",
            },
        ],
        "rules": [
            "nunca salvar token em JSON",
            "nunca imprimir token em log",
            "referenciar segredo como vault://env/NOME_DA_VARIAVEL",
            "API externa so pode rodar com credential_vault_ref",
            "publicacao oficial continua bloqueada ate Level 4",
        ],
    }
