# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

from k_atlas.social.social_orchestrator import SocialOrchestrator


def main() -> None:
    orchestrator = SocialOrchestrator()

    result = orchestrator.plan_social_operation(
        product="BRICS Paraguay Autos",
        market="marketplace automotivo Paraguai-Brasil",
        personas=[
            "compradores brasileiros interessados em carros no Paraguai",
            "lojistas paraguaios que precisam melhorar anuncios",
            "investidores buscando oportunidades automotivas regionais"
        ],
        objective="validar campanha local supervisionada para captacao inicial",
        channels=["Instagram", "Facebook", "WhatsApp"],
        duration_days=5,
        key_messages=[
            "anuncios automotivos mais claros e confiaveis",
            "revisao humana antes de qualquer publicacao",
            "ponte comercial entre Paraguai e Brasil com mais organizacao"
        ],
        format_type="reel",
        brand_tone="premium, confiavel e direto",
        region="Paraguai e Brasil",
        language="pt-BR",
        seasonal_context="campanha inicial de validacao comercial"
    )

    output_path = Path("k_atlas/social/reports/social_demo_operation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print("Relatorio gerado em:", output_path)
    print("Status:", result["operation_status"])
    print("Auditoria:", result["audit"]["audit_status"])
    print("Publicacao automatica:", result["publication_permission"])
    print("Revisao humana obrigatoria:", result["human_review_required"])


if __name__ == "__main__":
    main()
