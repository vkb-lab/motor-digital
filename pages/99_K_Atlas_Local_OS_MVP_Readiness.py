from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_os_mvp_readiness.readiness import LocalOSMVPReadiness


st.set_page_config(page_title="K-Atlas Local OS MVP Readiness", layout="wide")

st.title("K-Atlas Local OS MVP Readiness")
st.caption("Checkpoint 99 - verifica se o Local OS assistido esta pronto como MVP supervisionado.")

readiness = LocalOSMVPReadiness()
report = readiness.build_report()
summary = report.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Componentes", summary.get("components_total", 0))

with col2:
    st.metric("Operacionais", summary.get("components_operational", 0))

with col3:
    st.metric("Readiness", summary.get("readiness_score", 0))

with col4:
    st.metric("Local OS ready", str(summary.get("local_os_ready", False)))

st.divider()

tab_components, tab_guardrails, tab_report = st.tabs(["Componentes", "Guardrails", "Relatorio"])

with tab_components:
    for item in report.get("components", []):
        with st.expander(f"{item.get('checkpoint')} | {item.get('name')} | {item.get('status')}"):
            st.write(item.get("role"))
            st.json(item)

with tab_guardrails:
    for item in report.get("guardrails", []):
        st.write(f"- {item}")

with tab_report:
    st.json(report)
