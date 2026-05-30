from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.social.instagram_graph_readiness.policy import validate_instagram_payload
from k_atlas.social.instagram_graph_readiness.readiness import InstagramGraphReadiness


REPORT = Path("reports/instagram_graph_readiness/latest_instagram_graph_readiness.json")

st.set_page_config(page_title="K-Atlas Instagram Graph Readiness", layout="wide")

st.title("K-Atlas Instagram Graph Readiness")
st.caption("Prepara a integração do Instagram oficial K-Atlas. Sem chamada real. Sem publicação automática.")

readiness = InstagramGraphReadiness()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
summary = latest.get("summary", {}) if latest else {}

if st.button("Gerar readiness Instagram", type="primary"):
    result = readiness.generate()
    st.success("Readiness Instagram gerado.")
    st.json(result)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Env OK", f"{summary.get('configured_env_vars', 0)}/{summary.get('required_env_vars', 0)}")

with col3:
    st.metric("Live API", str(summary.get("live_call_enabled", False)))

with col4:
    st.metric("Publishing", str(summary.get("publishing_enabled", False)))

st.divider()

tab_summary, tab_env, tab_checklist, tab_permissions, tab_contract, tab_report = st.tabs([
    "Resumo",
    "Env",
    "Checklist",
    "Permissões",
    "Contrato de conteúdo",
    "Relatório",
])

with tab_summary:
    if not latest:
        st.warning("Nenhum readiness ainda. Clique em Gerar readiness Instagram.")
    else:
        st.info(summary.get("next_action", "sem próxima ação"))
        st.json(summary)

with tab_env:
    if not latest:
        st.info("Sem env status.")
    else:
        for item in latest.get("env_status", []):
            st.write(f"- {item.get('name')}: {item.get('value_preview')}")

with tab_checklist:
    if not latest:
        st.info("Sem checklist.")
    else:
        for item in latest.get("connection_checklist", []):
            with st.expander(f"{item.get('step')} | {item.get('title')} | {item.get('status')}"):
                st.json(item)

with tab_permissions:
    if not latest:
        st.info("Sem matriz de permissões.")
    else:
        for item in latest.get("permissions_matrix", []):
            with st.expander(f"{item.get('capability')} | {item.get('risk')}"):
                st.json(item)

with tab_contract:
    if latest:
        st.json(latest.get("content_contract", {}))
    else:
        st.info("Sem contrato ainda.")

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
