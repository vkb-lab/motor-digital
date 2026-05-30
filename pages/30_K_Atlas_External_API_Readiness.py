from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.external_api_adapter.readiness import ExternalAPIAdapterReadiness


REPORT = Path("reports/external_api_adapter/latest_external_api_adapter_readiness.json")

st.set_page_config(page_title="K-Atlas External API Readiness", layout="wide")

st.title("K-Atlas External API Adapter Readiness")
st.caption("Preparação segura para APIs reais. Sem chamada externa real. Sem token em arquivo.")

if st.button("Gerar readiness", type="primary"):
    result = ExternalAPIAdapterReadiness().generate()
    st.success("Readiness gerado.")
    st.json(result)

latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Providers", summary.get("providers_total", 0))

with col2:
    st.metric("Credenciais OK", summary.get("credentials_configured", 0))

with col3:
    st.metric("Ausentes", summary.get("credentials_missing", 0))

with col4:
    st.metric("Live API", str(summary.get("live_external_calls_enabled", False)))

st.divider()

tab_summary, tab_providers, tab_guardrails, tab_report = st.tabs(["Resumo", "Providers", "Guardrails", "Relatório"])

with tab_summary:
    if not latest:
        st.warning("Nenhum readiness ainda. Clique em Gerar readiness.")
    else:
        st.info(summary.get("next_action", "sem próxima ação"))
        st.json(summary)

with tab_providers:
    if not latest:
        st.info("Sem providers ainda.")
    else:
        for item in latest.get("providers", []):
            with st.expander(f"{item.get('provider')} | {item.get('status')}"):
                st.json(item)

with tab_guardrails:
    if not latest:
        st.info("Sem guardrails ainda.")
    else:
        for item in latest.get("guardrails", []):
            st.write(f"- {item}")

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
