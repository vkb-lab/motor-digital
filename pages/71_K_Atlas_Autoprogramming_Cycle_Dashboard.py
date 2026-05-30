from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autoprogramming_cycle_dashboard.dashboard import AutoprogrammingCycleDashboard


st.set_page_config(page_title="K-Atlas Autoprogramming Cycle", layout="wide")

st.title("K-Atlas Autoprogramming Cycle Dashboard")
st.caption("Painel do ciclo: proposta -> revisao -> pacote -> gate -> apply manual -> rollback manual.")

dashboard = AutoprogrammingCycleDashboard()
report = dashboard.build_report()
summary = report.get("summary", {})
queues = report.get("queues", {})
cowork = report.get("cowork", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Checkpoints", summary.get("checkpoints_total", 0))

with col2:
    st.metric("Operacionais", summary.get("checkpoints_operational", 0))

with col3:
    st.metric("Cycle ready", str(summary.get("cycle_ready", False)))

with col4:
    st.metric("Execucao externa", "False")

st.divider()

tab_cycle, tab_queues, tab_cowork, tab_report = st.tabs([
    "Ciclo",
    "Filas",
    "Cowork",
    "Relatorio",
])

with tab_cycle:
    st.subheader("Mapa do ciclo")
    for item in report.get("checkpoints", []):
        with st.expander(f"{item.get('checkpoint')} | {item.get('name')} | {item.get('status')}"):
            st.write(f"Funcao: {item.get('role')}")
            st.json(item)

with tab_queues:
    st.subheader("Estado operacional")
    q1, q2, q3, q4, q5 = st.columns(5)

    with q1:
        st.metric("Reviews", queues.get("review_queue", 0))
    with q2:
        st.metric("Packages", queues.get("apply_package_queue", 0))
    with q3:
        st.metric("Gate", queues.get("apply_package_gate_queue", 0))
    with q4:
        st.metric("Applies", queues.get("manual_apply_manifest", 0))
    with q5:
        st.metric("Rollbacks", queues.get("manual_rollback_manifest", 0))

with tab_cowork:
    st.subheader("Evidencia cowork")
    st.json(cowork)

with tab_report:
    st.subheader("Relatorio completo")
    if st.button("Reconstruir relatorio", type="primary"):
        report = dashboard.build_report()
        st.success("Relatorio reconstruido.")
    st.json(report)
