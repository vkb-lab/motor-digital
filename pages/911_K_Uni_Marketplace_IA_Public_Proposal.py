from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DIAG_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_public_lead_diagnostic.json"
PROPOSAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_public_commercial_proposal.json"
PROPOSAL_MD_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_public_commercial_proposal.md"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def build_proposal(diagnostic: dict) -> dict:
    recommendations = diagnostic.get("recommendations", [])

    return {
        "ok": True,
        "proposal_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "marketplace_ia_public_approved_lead_proposal",
        "diagnostic_id": diagnostic.get("diagnostic_id"),
        "lead_id": diagnostic.get("lead_id"),
        "external_send_enabled": False,
        "human_review_required": True,
        "title": "Proposta Comercial - IA Aplicada ao Negocio",
        "offer": {
            "name": "Plano IA Aplicada Starter",
            "positioning": "Implementacao assistida da primeira automacao de IA com diagnostico, priorizacao e governanca.",
            "deliverables": [
                "Revisao do diagnostico aprovado",
                "Mapa com 3 oportunidades de automacao",
                "Priorizacao por impacto e facilidade",
                "Implementacao da primeira automacao validada",
                "Painel simples de acompanhamento",
                "Rotina de revisao e proximos passos"
            ],
            "suggested_price_range": "R$ 497 a R$ 1.997",
            "commercial_note": "Faixa inicial sugerida. Valor final depende do escopo aprovado manualmente."
        },
        "recommended_automations": recommendations,
        "next_step": "Enviar para Approval Gate da proposta publica antes de qualquer contato externo."
    }


def proposal_to_md(proposal: dict) -> str:
    offer = proposal.get("offer", {})
    lines = [
        "# Proposta Comercial - IA Aplicada ao Negocio",
        "",
        "## Oferta",
        "",
        f"**{offer.get('name', '')}**",
        "",
        offer.get("positioning", ""),
        "",
        "## Entregaveis",
        "",
    ]

    for item in offer.get("deliverables", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Automacoes recomendadas",
        "",
    ])

    for index, item in enumerate(proposal.get("recommended_automations", []), start=1):
        lines.append(f"### {index}. {item.get('name')}")
        lines.append("")
        lines.append(item.get("description", ""))
        lines.append("")
        lines.append(f"- Impacto: {item.get('impact')}")
        lines.append(f"- Esforco: {item.get('effort')}")
        lines.append("")

    lines.extend([
        "## Faixa sugerida",
        "",
        offer.get("suggested_price_range", "A definir"),
        "",
        "## Seguranca operacional",
        "",
        "- Envio automatico bloqueado",
        "- Revisao humana obrigatoria",
        "- Dados mantidos localmente",
        "- Proposta ainda nao enviada",
    ])

    return "\n".join(lines)


st.set_page_config(
    page_title="Marketplace IA - Proposta Publica Aprovada",
    layout="wide",
)

st.title("Marketplace IA - Proposta do Lead Publico Aprovado")
st.caption("Test Mission 011 - proposta local baseada no diagnostico publico aprovado.")

diagnostic = load_json(DIAG_PATH)

if not diagnostic:
    st.warning("Nenhum diagnostico publico aprovado encontrado.")
    st.stop()

st.header("Diagnostico base")

st.json({
    "diagnostic_id": diagnostic.get("diagnostic_id"),
    "lead_id": diagnostic.get("lead_id"),
    "source": diagnostic.get("source"),
    "review_gate_status": diagnostic.get("review_gate_status"),
    "external_send_enabled": diagnostic.get("external_send_enabled"),
    "recommendations_count": len(diagnostic.get("recommendations", [])),
})

proposal = build_proposal(diagnostic)
offer = proposal.get("offer", {})

st.divider()
st.header("Proposta sugerida")

left, right = st.columns([1.2, 1])

with left:
    st.subheader(offer.get("name"))
    st.write(offer.get("positioning"))

    st.markdown("### Entregaveis")
    for item in offer.get("deliverables", []):
        st.write("- " + item)

    st.markdown("### Faixa sugerida")
    st.success(offer.get("suggested_price_range"))

with right:
    st.markdown("### Automacoes recomendadas")
    for index, item in enumerate(proposal.get("recommended_automations", []), start=1):
        with st.expander(f"{index}. {item.get('name')}", expanded=True):
            st.write(item.get("description"))
            st.write(f"Impacto: {item.get('impact')}")
            st.write(f"Esforco: {item.get('effort')}")

st.divider()

if st.button("Salvar proposta publica local", type="primary"):
    PROPOSAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    PROPOSAL_PATH.write_text(
        json.dumps(proposal, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    PROPOSAL_MD_PATH.write_text(
        proposal_to_md(proposal),
        encoding="utf-8"
    )

    st.success("Proposta publica salva localmente. Nenhum envio externo foi feito.")
    st.json(proposal)

if PROPOSAL_MD_PATH.exists():
    st.divider()
    st.subheader("Markdown da proposta")
    st.code(PROPOSAL_MD_PATH.read_text(encoding="utf-8-sig"), language="markdown")

st.caption("Dados sensiveis continuam locais em live/marketplace_ia/.")