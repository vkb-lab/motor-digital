from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEADS_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "lead_intake.jsonl"
DIAG_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "latest_lead_diagnostic.json"


def load_latest_lead() -> dict | None:
    if not LEADS_PATH.exists():
        return None

    rows = [
        line.strip()
        for line in LEADS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    if not rows:
        return None

    return json.loads(rows[-1])


def build_recommendations(lead: dict) -> list[dict]:
    objetivo = str(lead.get("objetivo", "")).lower()
    segmento = str(lead.get("segmento", "")).lower()
    desafio = str(lead.get("desafio", "")).lower()

    recommendations = []

    if "vender" in objetivo or "comercial" in desafio:
        recommendations.append({
            "name": "Agente de follow-up comercial",
            "impact": "alto",
            "effort": "medio",
            "description": "Criar um fluxo assistido para responder leads, organizar conversas e sugerir próximos passos comerciais."
        })

    if "conteudo" in objetivo or "conteudo" in desafio:
        recommendations.append({
            "name": "Esteira de conteúdo com IA",
            "impact": "alto",
            "effort": "baixo",
            "description": "Gerar calendário, posts, legendas e roteiros com aprovação humana antes de publicar."
        })

    if "atendimento" in objetivo or "tempo" in objetivo or "tempo" in desafio:
        recommendations.append({
            "name": "Automação de atendimento inicial",
            "impact": "alto",
            "effort": "medio",
            "description": "Criar triagem automática para dúvidas frequentes, captura de dados e encaminhamento para atendimento humano."
        })

    if "saas" in objetivo or "saas" in segmento:
        recommendations.append({
            "name": "Blueprint de SaaS validável",
            "impact": "alto",
            "effort": "alto",
            "description": "Transformar a ideia em escopo de MVP, módulos, landing page e plano de validação."
        })

    if len(recommendations) < 3:
        recommendations.append({
            "name": "Dashboard operacional simples",
            "impact": "medio",
            "effort": "baixo",
            "description": "Centralizar tarefas, leads, próximos passos e indicadores em um painel local."
        })

    if len(recommendations) < 3:
        recommendations.append({
            "name": "Gerador de propostas com IA",
            "impact": "medio",
            "effort": "baixo",
            "description": "Criar propostas comerciais padronizadas a partir do tipo de cliente e necessidade."
        })

    return recommendations[:3]


st.set_page_config(page_title="Marketplace IA - Diagnóstico", layout="wide")

st.title("Marketplace IA - Diagnóstico Local do Lead")
st.caption("Teste real 003 - análise local supervisionada. Nenhum envio externo.")

lead = load_latest_lead()

if not lead:
    st.warning("Nenhum lead encontrado em live/marketplace_ia/lead_intake.jsonl")
    st.stop()

st.subheader("Lead analisado localmente")

safe_lead = {
    "segmento": lead.get("segmento"),
    "objetivo": lead.get("objetivo"),
    "desafio": lead.get("desafio"),
    "source": lead.get("source"),
    "status": lead.get("status"),
}

st.json(safe_lead)

recommendations = build_recommendations(lead)

st.divider()
st.subheader("3 automações recomendadas")

for index, item in enumerate(recommendations, start=1):
    with st.expander(f"{index}. {item['name']}", expanded=True):
        st.write(item["description"])
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Impacto", item["impact"])
        with c2:
            st.metric("Esforço", item["effort"])

if st.button("Gerar diagnóstico local", type="primary"):
    DIAG_PATH.parent.mkdir(parents=True, exist_ok=True)

    diagnostic = {
        "ok": True,
        "diagnostic_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lead_id": lead.get("lead_id"),
        "source": "marketplace_ia_local_diagnostic",
        "external_send_enabled": False,
        "human_review_required": True,
        "recommendations": recommendations,
        "next_step": "Revisar diagnóstico e transformar em proposta comercial local."
    }

    DIAG_PATH.write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2), encoding="utf-8")

    st.success("Diagnóstico salvo localmente. Nenhum envio externo foi feito.")
    st.json(diagnostic)

if DIAG_PATH.exists():
    st.divider()
    st.subheader("Último diagnóstico salvo")
    st.json(json.loads(DIAG_PATH.read_text(encoding="utf-8-sig")))

st.caption("Dados sensíveis permanecem locais em live/marketplace_ia/")
