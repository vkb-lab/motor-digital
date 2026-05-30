from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROPOSAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_public_commercial_proposal.json"
APPROVAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "public_proposal_approval_decision.json"
SEND_PACK_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "public_manual_send_pack.md"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def build_manual_send_pack(proposal: dict, notes: str) -> str:
    offer = proposal.get("offer", {})
    recommendations = proposal.get("recommended_automations", [])

    lines = [
        "# Pacote Manual de Envio - Lead Publico Marketplace IA",
        "",
        "Status: aprovado localmente",
        "",
        "## Mensagem curta",
        "",
        "Olá! Preparei um diagnóstico inicial com oportunidades práticas de IA para o seu negócio.",
        "",
        "A proposta inicial é começar com um plano simples para mapear o processo, priorizar automações e implementar a primeira com acompanhamento.",
        "",
        "## Oferta",
        "",
        f"**{offer.get('name', 'Plano IA Aplicada Starter')}**",
        "",
        offer.get("positioning", ""),
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
        "## Segurança operacional",
        "",
        "- Envio automático bloqueado",
        "- WhatsApp bloqueado",
        "- Email bloqueado",
        "- Instagram bloqueado",
        "- Copiar e enviar manualmente somente após revisão final",
    ])

    return "\n".join(lines)


st.set_page_config(
    page_title="Marketplace IA - Approval Gate Proposta Publica",
    layout="wide",
)

st.title("Marketplace IA - Approval Gate da Proposta Publica")
st.caption("Test Mission 012 - revisão humana antes de qualquer envio comercial.")

proposal = load_json(PROPOSAL_PATH)

if not proposal:
    st.warning("Nenhuma proposta pública local encontrada.")
    st.stop()

st.warning("Nenhum envio externo será feito. Este gate apenas registra aprovação local e gera pacote manual.")

offer = proposal.get("offer", {})

st.header("Resumo comercial")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Oferta", offer.get("name", "N/A"))

with c2:
    st.metric("Faixa", offer.get("suggested_price_range", "N/A"))

with c3:
    st.metric("Envio externo", "BLOQUEADO")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Proposta")

    st.markdown("### Posicionamento")
    st.write(offer.get("positioning", ""))

    st.markdown("### Entregáveis")
    for item in offer.get("deliverables", []):
        st.write("- " + item)

    st.markdown("### Automações recomendadas")
    for index, item in enumerate(proposal.get("recommended_automations", []), start=1):
        with st.expander(f"{index}. {item.get('name')}", expanded=True):
            st.write(item.get("description"))
            st.write(f"Impacto: {item.get('impact')}")
            st.write(f"Esforço: {item.get('effort')}")

with right:
    st.subheader("Decisão do operador")

    approved = st.checkbox("Aprovar proposta pública localmente")
    notes = st.text_area("Observações antes do envio manual")

    if st.button("Registrar aprovação e gerar pacote manual", type="primary"):
        APPROVAL_PATH.parent.mkdir(parents=True, exist_ok=True)

        decision = {
            "ok": True,
            "decision": "approved_local_only" if approved else "pending_review",
            "proposal_id": proposal.get("proposal_id"),
            "lead_id": proposal.get("lead_id"),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "external_send_enabled": False,
            "manual_send_required": True,
            "human_approval_recorded": approved,
        }

        APPROVAL_PATH.write_text(
            json.dumps(decision, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        if approved:
            SEND_PACK_PATH.write_text(
                build_manual_send_pack(proposal, notes),
                encoding="utf-8"
            )
            st.success("Proposta pública aprovada localmente. Pacote manual gerado.")
        else:
            st.info("Proposta ficou pendente de revisão.")

        st.json(decision)

    if st.button("Reprovar proposta pública"):
        decision = {
            "ok": True,
            "decision": "rejected",
            "proposal_id": proposal.get("proposal_id"),
            "lead_id": proposal.get("lead_id"),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "external_send_enabled": False,
            "manual_send_required": False,
            "human_approval_recorded": True,
        }

        APPROVAL_PATH.write_text(
            json.dumps(decision, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        st.error("Proposta pública reprovada localmente.")
        st.json(decision)

if APPROVAL_PATH.exists():
    st.divider()
    st.subheader("Última decisão")
    st.json(load_json(APPROVAL_PATH))

if SEND_PACK_PATH.exists():
    st.divider()
    st.subheader("Pacote manual de envio")
    st.code(SEND_PACK_PATH.read_text(encoding="utf-8-sig"), language="markdown")

st.caption("Dados e pacote permanecem locais em live/marketplace_ia/.")