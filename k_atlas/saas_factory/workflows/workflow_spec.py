from __future__ import annotations

from typing import Any, Mapping


def build_default_saas_workflow_payload() -> dict[str, Any]:
    return {
        "product_name": "K-Atlas Local Business Copilot",
        "audience": "negocios locais, prestadores de servico e operadores comerciais",
        "problem": "falta de cockpit simples para leads, tarefas, campanhas e relatorios",
        "solution": "SaaS MVP em Streamlit com dashboard, CRM leve, campanhas, relatorios e admin",
        "monetization": "setup inicial + assinatura mensal",
        "modules": [
            "dashboard",
            "lead_capture",
            "crm_light",
            "campaigns",
            "reports",
            "admin",
        ],
        "governance": {
            "human_review_required": True,
            "external_api_enabled": False,
            "official_publish": False,
            "auto_deploy": False,
        },
    }


def validate_saas_workflow_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    if not str(data.get("product_name", "")).strip():
        reasons.append("product_name_required")

    if data.get("external_api_enabled") is True:
        reasons.append("external_api_blocked_in_checkpoint_38")

    if data.get("official_publish") is True:
        reasons.append("official_publish_blocked")

    if data.get("auto_deploy") is True:
        reasons.append("auto_deploy_blocked")

    if data.get("token") or data.get("api_key") or data.get("password"):
        reasons.append("plaintext_secret_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "valid" if not reasons else "blocked",
        "reasons": reasons or ["payload_valid_for_saas_factory_workflow"],
    }
