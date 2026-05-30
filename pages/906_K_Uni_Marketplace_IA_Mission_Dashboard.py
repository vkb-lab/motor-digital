from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "lead_intake": PROJECT_ROOT / "live" / "marketplace_ia" / "lead_intake.jsonl",
    "instagram_approval": PROJECT_ROOT / "live" / "marketplace_ia" / "instagram_approval_decision.json",
    "diagnostic": PROJECT_ROOT / "live" / "marketplace_ia" / "latest_lead_diagnostic.json",
    "proposal": PROJECT_ROOT / "live" / "marketplace_ia" / "latest_commercial_proposal.json",
    "proposal_approval": PROJECT_ROOT / "live" / "marketplace_ia" / "proposal_approval_decision.json",
    "manual_send_pack": PROJECT_ROOT / "live" / "marketplace_ia" / "manual_send_pack.md",
}


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return len([line for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()])


def ok_label(value: bool) -> str:
    return "OK" if value else "PENDENTE"


st.set_page_config(page_title="Marketplace IA Mission Dashboard", layout="wide")

st.title("Marketplace IA - Mission Dashboard")
st.caption("Test Mission 006 - painel consolidado do fluxo comercial local.")

lead_count = count_jsonl(PATHS["lead_intake"])
instagram_approval = load_json(PATHS["instagram_approval"])
diagnostic = load_json(PATHS["diagnostic"])
proposal = load_json(PATHS["proposal"])
proposal_approval = load_json(PATHS["proposal_approval"])
manual_pack_exists = PATHS["manual_send_pack"].exists()

st.header("Status do Funil")

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.metric("Leads", lead_count)
with c2:
    st.metric("Instagram", ok_label(bool(instagram_approval)))
with c3:
    st.metric("Diagnostico", ok_label(bool(diagnostic)))
with c4:
    st.metric("Proposta", ok_label(bool(proposal)))
with c5:
    st.metric("Aprovacao", ok_label(bool(proposal_approval)))
with c6:
    st.metric("Pacote", ok_label(manual_pack_exists))

st.divider()

st.header("Resumo Operacional")

left, right = st.columns([1.1, 1])

with left:
    st.subheader("Checklist")

    checklist = {
        "Landing Marketplace IA criada": True,
        "Lead capturado localmente": lead_count > 0,
        "Campanha Instagram aprovada localmente": bool(instagram_approval),
        "Diagnostico local gerado": bool(diagnostic),
        "Proposta comercial salva": bool(proposal),
        "Proposta aprovada localmente": bool(proposal_approval),
        "Pacote manual gerado": manual_pack_exists,
        "Envio externo bloqueado": True,
        "Dados sensiveis fora do GitHub": True,
    }

    for item, status in checklist.items():
        st.write(f"{ok_label(status)} - {item}")

with right:
    st.subheader("Governanca")

    st.info("Este painel apenas lê artefatos locais. Nenhum envio externo é executado.")
    st.write("Pasta sensivel: live/marketplace_ia/")
    st.write("Status: ignorada pelo Git.")
    st.write("Publicacao Instagram: bloqueada.")
    st.write("WhatsApp/API externa: bloqueados.")
    st.write("Envio comercial: manual.")

st.divider()

st.header("Detalhes")

tab1, tab2, tab3, tab4 = st.tabs(["Instagram", "Diagnostico", "Proposta", "Pacote Manual"])

with tab1:
    if instagram_approval:
        st.json(instagram_approval)
    else:
        st.warning("Aprovacao Instagram ainda nao encontrada.")

with tab2:
    if diagnostic:
        st.json({
            "diagnostic_id": diagnostic.get("diagnostic_id"),
            "recommendations_count": len(diagnostic.get("recommendations", [])),
            "external_send_enabled": diagnostic.get("external_send_enabled"),
            "next_step": diagnostic.get("next_step"),
        })

        for index, item in enumerate(diagnostic.get("recommendations", []), start=1):
            with st.expander(f"{index}. {item.get('name')}", expanded=False):
                st.write(item.get("description"))
                st.write(f"Impacto: {item.get('impact')}")
                st.write(f"Esforco: {item.get('effort')}")
    else:
        st.warning("Diagnostico ainda nao encontrado.")

with tab3:
    if proposal:
        offer = proposal.get("offer", {})
        st.json({
            "proposal_id": proposal.get("proposal_id"),
            "offer": offer.get("name"),
            "price_range": offer.get("suggested_price_range"),
            "external_send_enabled": proposal.get("external_send_enabled"),
            "human_review_required": proposal.get("human_review_required"),
        })

        if proposal_approval:
            st.subheader("Decisao")
            st.json(proposal_approval)
    else:
        st.warning("Proposta ainda nao encontrada.")

with tab4:
    if manual_pack_exists:
        st.code(PATHS["manual_send_pack"].read_text(encoding="utf-8-sig"), language="markdown")
    else:
        st.warning("Pacote manual ainda nao encontrado.")

st.divider()

st.header("Proximo Passo Recomendado")

if all([
    lead_count > 0,
    bool(instagram_approval),
    bool(diagnostic),
    bool(proposal),
    bool(proposal_approval),
    manual_pack_exists,
]):
    st.success("Fluxo local validado. Proximo: criar landing publica sanitizada sem dados sensiveis.")
else:
    st.warning("Ainda existem etapas pendentes antes da landing publica.")

st.caption("K-Uni Marketplace IA - fluxo local supervisionado.")