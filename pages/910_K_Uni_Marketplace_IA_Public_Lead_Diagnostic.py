from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LEAD_INTAKE_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "lead_intake.jsonl"
PUBLIC_REVIEW_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "public_capture_review_decision.json"
PUBLIC_DIAG_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_public_lead_diagnostic.json"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def load_jsonl_valid(path: Path) -> list[dict]:
    if not path.exists():
        return []

    rows = []

    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip().lstrip("\ufeff")
        if not line:
            continue

        try:
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
        except Exception:
            continue

    return rows


def latest_approved_lead() -> dict | None:
    leads = load_jsonl_valid(LEAD_INTAKE_PATH)

    approved = [
        lead for lead in leads
        if str(lead.get("status", "")).lower() in {
            "approved_for_local_diagnostic",
            "captured_local_only",
            "captured_public_local_only_recovered",
        }
    ]

    if approved:
        return approved[-1]

    if leads:
        return leads[-1]

    return None


def build_recommendations(lead: dict) -> list[dict]:
    objetivo = str(lead.get("objetivo", "")).lower()
    segmento = str(lead.get("segmento", "")).lower()
    desafio = str(lead.get("desafio", "")).lower()

    items = []

    if "vender" in objetivo or "venda" in desafio or "comercial" in desafio:
        items.append({
            "name": "Agente de follow-up comercial",
            "impact": "alto",
            "effort": "medio",
            "description": "Organizar respostas, próximos passos e acompanhamento comercial para leads capturados."
        })

    if "conteudo" in objetivo or "conteudo" in desafio or "criador" in segmento:
        items.append({
            "name": "Esteira de conteúdo com aprovação humana",
            "impact": "alto",
            "effort": "baixo",
            "description": "Criar calendário, posts, legendas e campanhas com revisão antes de publicar."
        })

    if "atendimento" in objetivo or "tempo" in objetivo or "tempo" in desafio:
        items.append({
            "name": "Triagem automatizada de atendimento",
            "impact": "alto",
            "effort": "medio",
            "description": "Capturar dados iniciais, responder dúvidas frequentes e encaminhar casos para atendimento humano."
        })

    if "saas" in objetivo or "saas" in segmento:
        items.append({
            "name": "Blueprint de MVP SaaS com IA",
            "impact": "alto",
            "effort": "alto",
            "description": "Transformar a oportunidade em escopo de produto, módulos e plano de validação."
        })

    defaults = [
        {
            "name": "Dashboard operacional de leads",
            "impact": "medio",
            "effort": "baixo",
            "description": "Centralizar leads, status, diagnóstico, proposta e próximos passos em um painel simples."
        },
        {
            "name": "Gerador de proposta comercial",
            "impact": "medio",
            "effort": "baixo",
            "description": "Transformar diagnóstico em proposta inicial pronta para revisão manual."
        },
        {
            "name": "Rotina semanal de otimização com IA",
            "impact": "medio",
            "effort": "baixo",
            "description": "Revisar oportunidades, gargalos e ações recomendadas semanalmente."
        },
    ]

    for item in defaults:
        if len(items) >= 3:
            break
        if item["name"] not in [x["name"] for x in items]:
            items.append(item)

    return items[:3]


st.set_page_config(
    page_title="Marketplace IA - Diagnóstico Público Aprovado",
    layout="wide",
)

st.title("Marketplace IA - Diagnóstico do Lead Público Aprovado")
st.caption("Test Mission 010 - diagnóstico local após review humano.")

review = load_json(PUBLIC_REVIEW_PATH)
lead = latest_approved_lead()

if not lead:
    st.warning("Nenhum lead aprovado encontrado em live/marketplace_ia/lead_intake.jsonl")
    st.stop()

st.header("Gate anterior")

if review:
    st.json({
        "decision": review.get("decision"),
        "lead_id": review.get("lead_id"),
        "external_send_enabled": review.get("external_send_enabled"),
        "human_review_recorded": review.get("human_review_recorded"),
    })
else:
    st.info("Review anterior não encontrado, mas existe lead local para diagnóstico.")

st.divider()

st.header("Lead aprovado para diagnóstico")

safe_lead = {
    "lead_id": lead.get("lead_id"),
    "negocio": lead.get("negocio"),
    "segmento": lead.get("segmento"),
    "objetivo": lead.get("objetivo"),
    "desafio": lead.get("desafio"),
    "source": lead.get("source"),
    "status": lead.get("status"),
    "external_send_enabled": lead.get("external_send_enabled"),
    "human_review_required": lead.get("human_review_required"),
}

st.json(safe_lead)

recommendations = build_recommendations(lead)

st.divider()
st.header("3 automações recomendadas")

for index, item in enumerate(recommendations, start=1):
    with st.expander(f"{index}. {item['name']}", expanded=True):
        st.write(item["description"])

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Impacto", item["impact"])
        with c2:
            st.metric("Esforço", item["effort"])

st.divider()

if st.button("Salvar diagnóstico público aprovado", type="primary"):
    PUBLIC_DIAG_PATH.parent.mkdir(parents=True, exist_ok=True)

    diagnostic = {
        "ok": True,
        "diagnostic_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lead_id": lead.get("lead_id"),
        "source": "marketplace_ia_public_approved_lead_diagnostic",
        "review_gate_required": True,
        "review_gate_status": review.get("decision") if review else "unknown",
        "external_send_enabled": False,
        "human_review_required": True,
        "recommendations": recommendations,
        "next_step": "Gerar proposta comercial local para o lead público aprovado."
    }

    PUBLIC_DIAG_PATH.write_text(
        json.dumps(diagnostic, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    st.success("Diagnóstico público aprovado salvo localmente.")
    st.json(diagnostic)

if PUBLIC_DIAG_PATH.exists():
    st.divider()
    st.subheader("Último diagnóstico público aprovado")
    st.json(load_json(PUBLIC_DIAG_PATH))

st.caption("Nenhum envio externo. Dados continuam locais em live/marketplace_ia/.")