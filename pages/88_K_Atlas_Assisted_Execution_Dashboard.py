from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.assisted_execution_dashboard.dashboard import AssistedExecutionDashboard

st.set_page_config(page_title="K-Atlas Assisted Execution", layout="wide")
st.title("K-Atlas Assisted Execution Dashboard")
st.caption("Camada de execucao assistida: contratos, roteador, fila e auditoria.")

dashboard = AssistedExecutionDashboard()
report = dashboard.build_report()
summary = report.get("summary", {})

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Contratos", summary.get("contracts_total", 0))
with c2:
    st.metric("Rotas", summary.get("routes_total", 0))
with c3:
    st.metric("Fila", summary.get("execution_queue_total", 0))
with c4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()

tabs = st.tabs(["Resumo", "Contratos", "Router", "Fila", "Auditoria", "Guardrails"])

with tabs[0]:
    st.json(summary)
with tabs[1]:
    st.json(report.get("contracts"))
with tabs[2]:
    st.json(report.get("router"))
with tabs[3]:
    st.json(report.get("execution_queue"))
with tabs[4]:
    st.json(report.get("ledger"))
with tabs[5]:
    st.json(report.get("guardrails"))
