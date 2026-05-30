from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_commercial_proposal.json"
PROPOSAL_MD_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_commercial_proposal.md"
APPROVAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "proposal_approval_decision.json"
SEND_PACK_PATH = PROJECT_ROOT / "content_packs" / "marketplace_ia" / "manual_send_pack.md"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_send_pack(proposal: dict, notes: str) -> str:
    offer = proposal.get("offer", {})
    recommendations = proposal.get("recommended_automations", [])

    lines = [
        "# Pacote Manual de Envio - Marketplace IA",
        "",
        "Status: aprovado localmente",
        "",
        "## Mensagem curta",
        "",
        "Olá! Preparei um diagnóstico inicial com oportunidades práticas de IA para o seu negócio.",
        "",
        "A proposta inicial é começar com um plano simples para mapear o processo, priorizar 3 automações e implementar a primeira com acompanhamento.",
        "",
        "## Oferta",
        "",
        f"**{offer.get('name', 'Plano IA Aplicada Starter')}**",
        "",
        offer.get("promise", ""),
        "",
        "## Entregáveis",
        "",
    ]

    for item in offer.get("deliverables", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Faixa sugerida",
        "",
        offer.get("suggested_price_range", "A definir"),
        "",
        "## Automações recomendadas",
        "",
    ])

    for index, item in enumerate(recommendations, start=1):
        lines.append(f"{index}. {item.get('name')}")
        lines.append(f"   - {item.get('description')}")
        lines.append(f"   - Impacto: {item.get('impact')}")
        lines.append(f"   - Esforço: {item.get('effort')}")
        lines.append("")

    lines.extend([
        "## Observações internas",
        "",
        notes or "Sem observações.",
        "",
        "## Segurança",
        "",
        "- Envio automático bloqueado",
        "- WhatsApp bloqueado",
        "- Email bloqueado",
        "- Instagram bloqueado",
        "- Envio deve ser manual pelo operador",
    ])

    return "\n".join(lines)


st.set_page_config(page_title="Marketplace IA - Aprovação da Proposta", layout="wide")

st.title("Marketplace IA - Approval Gate da Proposta")
st.caption("Teste real 005 - aprovação humana antes de qualquer envio comercial.")

proposal = load_json(PROPOSAL_PATH)

if not proposal:
    st.warning("Nenhuma proposta local encontrada. Salve a proposta primeiro na etapa 004.")
    st.stop()

st.warning("Nenhum envio externo será feito. Este portal apenas registra aprovação local e gera pacote manual.")

st.subheader("Resumo da proposta")

offer = proposal.get("offer", {})

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Oferta", offer.get("name", "N/A"))

with col2:
    st.metric("Faixa sugerida", offer.get("suggested_price_range", "N/A"))

with col3:
    st.metric("Envio externo", str(proposal.get("external_send_enabled", False)))

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.markdown("## Promessa")
    st.write(offer.get("promise", ""))

    st.markdown("## Entregáveis")
    for item in offer.get("deliverables", []):
        st.write("- " + item)

    st.markdown("## Automações recomendadas")
    for index, item in enumerate(proposal.get("recommended_automations", []), start=1):
        with st.expander(f"{index}. {item.get('name')}", expanded=True):
            st.write(item.get("description"))
            st.write(f"Impacto: {item.get('impact')}")
            st.write(f"Esforço: {item.get('effort')}")

with right:
    st.markdown("## Decisão do operador")

    approved = st.checkbox("Aprovar proposta localmente")
    notes = st.text_area("Observações antes do envio manual")

    if st.button("Registrar aprovação e gerar pacote manual", type="primary"):
        APPROVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        SEND_PACK_PATH.parent.mkdir(parents=True, exist_ok=True)

        decision = {
            "ok": True,
            "decision": "approved_local_only" if approved else "pending_review",
            "approved_at": datetime.now(timezone.utc).isoformat() if approved else None,
            "notes": notes,
            "external_send_enabled": False,
            "manual_send_required": True,
            "human_approval_recorded": approved,
            "proposal_id": proposal.get("proposal_id"),
        }

        APPROVAL_PATH.write_text(
            json.dumps(decision, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        if approved:
            SEND_PACK_PATH.write_text(
                build_send_pack(proposal, notes),
                encoding="utf-8"
            )
            st.success("Proposta aprovada localmente e pacote manual gerado.")
        else:
            st.info("Proposta ficou pendente de revisão.")

        st.json(decision)

    if st.button("Reprovar proposta"):
        APPROVAL_PATH.parent.mkdir(parents=True, exist_ok=True)

        decision = {
            "ok": True,
            "decision": "rejected",
            "rejected_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "external_send_enabled": False,
            "human_approval_recorded": True,
            "proposal_id": proposal.get("proposal_id"),
        }

        APPROVAL_PATH.write_text(
            json.dumps(decision, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        st.error("Proposta reprovada localmente.")
        st.json(decision)

if APPROVAL_PATH.exists():
    st.divider()
    st.subheader("Última decisão")
    st.json(load_json(APPROVAL_PATH))

if SEND_PACK_PATH.exists():
    st.divider()
    st.subheader("Pacote manual de envio")
    st.code(SEND_PACK_PATH.read_text(encoding="utf-8-sig"), language="markdown")

st.caption("Dados sensíveis continuam locais. Apenas a estrutura da missão vai para GitHub.")
