from __future__ import annotations

import json

from .builder import SaaSBuilderAgent


def export_default_mvp() -> dict:
    payload = {
        "product_name": "K-Atlas Demo SaaS",
        "audience": "founders, operadores e negocios locais",
        "problem": "falta de cockpit digital simples para validar operacoes com IA",
        "solution": "MVP Streamlit com dashboard, modulos e estado JSON",
        "monetization": "assinatura mensal + setup",
        "modules": ["dashboard", "lead_capture", "campaigns", "reports", "admin"],
    }
    return SaaSBuilderAgent().generate_app_module(payload)


if __name__ == "__main__":
    print(json.dumps(export_default_mvp(), ensure_ascii=False, indent=2))
