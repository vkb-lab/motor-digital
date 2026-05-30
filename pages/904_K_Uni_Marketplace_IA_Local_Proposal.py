from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAG_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_lead_diagnostic.json"
PROPOSAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_commercial_proposal.json"
PROPOSAL_MD_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_commercial_proposal.md"


def load_diagnostic() -> dict | None:
    if not DIAG_PATH.exists():
        return None
    return json.loads(DIAG_PATH.read_text(encoding="utf-8-sig"))


def build_proposal(diagnostic: dict) -> dict:
    recommendations = diagnostic.get("recommendations", [])

    return {
        "ok": True,
        "proposal_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "marketplace_ia_local_proposal",
        "external_send_enabled": False,
        "human_review_required": True,
        "title": "Proposta Inicial - Diagnostico e Automacoes de IA",
        "offer": {
            "name": "Plano IA Aplicada Starter",
            "promise": "Mapear, priorizar e implementar a primeira automacao de IA com seguranca e aprovacao humana.",
            "deliverables": [
                "Diagnostico pratico do processo atual",
                "Mapa com 3 oportunidades de automacao",
                "Priorizacao por impacto e facilidade",
                "Implementacao assistida da primeira automacao",
                "Painel simples para acompanhar proximos passos"
            ],
            "suggested_price_range": "R$ 497 a R$ 1.997",
            "payment_note": "Preco final depende do escopo aprovado pelo operador."
        },
        "recommended_automations": recommendations,
        "next_step": "Revisar proposta, ajustar preco e aprovar envio manual."
    }


def proposal_to_md(proposal: dict) -> str:
    lines = [
        "# Proposta Inicial - Diagnostico e Automacoes de IA",
        "",
        "## Oferta",
        "",
        f"**{proposal['offer']['name']}**",
        "",
        proposal["offer"]["promise"],
        "",
        "## Entregaveis",
        "",
    ]

    for item in proposal["offer"]["deliverables"]:
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
        proposal["offer"]["suggested_price_range"],
        "",
        "## Observacao",
        "",
        "Rascunho local. Nenhum envio externo foi feito.",
    ])

    return "\n".join(lines)


st.set_page_config(page_title="Marketplace IA - Proposta Local", layout="wide")

st.title("Marketplace IA - Proposta Comercial Local")
st.caption("Teste real 004 - proposta local baseada no diagnostico. Nenhum envio externo.")

diagnostic = load_diagnostic()

if not diagnostic:
    st.warning("Nenhum diagnostico encontrado. Gere primeiro o diagnostico local do lead.")
    st.stop()

st.subheader("Diagnostico usado como base")
st.json({
    "diagnostic_id": diagnostic.get("diagnostic_id"),
    "source": diagnostic.get("source"),
    "external_send_enabled": diagnostic.get("external_send_enabled"),
    "recommendations_count": len(diagnostic.get("recommendations", [])),
})

st.divider()

proposal = build_proposal(diagnostic)

st.subheader("Proposta gerada")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown(f"## {proposal['offer']['name']}")
    st.write(proposal["offer"]["promise"])

    st.markdown("### Entregaveis")
    for item in proposal["offer"]["deliverables"]:
        st.write("- " + item)

    st.markdown("### Faixa sugerida")
    st.success(proposal["offer"]["suggested_price_range"])

with col2:
    st.markdown("### Automacoes recomendadas")
    for index, item in enumerate(proposal["recommended_automations"], start=1):
        st.write(f"{index}. {item.get('name')}")

st.divider()

if st.button("Salvar proposta local", type="primary"):
    PROPOSAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    PROPOSAL_PATH.write_text(
        json.dumps(proposal, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    PROPOSAL_MD_PATH.write_text(
        proposal_to_md(proposal),
        encoding="utf-8"
    )

    st.success("Proposta salva localmente. Nenhum envio externo foi feito.")
    st.json(proposal)

if PROPOSAL_MD_PATH.exists():
    st.divider()
    st.subheader("Markdown da proposta")
    st.code(PROPOSAL_MD_PATH.read_text(encoding="utf-8-sig"), language="markdown")

st.caption("Dados e proposta ficam em live/marketplace_ia/, fora do GitHub.")
