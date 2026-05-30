from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.secure_local_api_dashboard.dashboard import SecureLocalApiDashboard


st.set_page_config(page_title="K-Atlas Secure Local API Dashboard", layout="wide")
st.title("K-Atlas Secure Local API Dashboard")
st.caption("Dashboard unificado da API local segura: runtime, policy, approval e audit.")

dashboard = SecureLocalApiDashboard()
report = dashboard.build_report()
summary = report.get("summary", {})

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Modulos", f"{summary.get('modules_ready')}/{summary.get('modules_total')}")
with col2:
    st.metric("Public access", str(summary.get("public_access_allowed")))
with col3:
    st.metric("Remote control", str(summary.get("remote_control_allowed")))
with col4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled")))

st.divider()

tab_modules, tab_runtime, tab_approval, tab_audit, tab_report = st.tabs([
    "Modulos", "Runtime", "Approval", "Audit", "Relatorio"
])

with tab_modules:
    st.json(report.get("modules"))

with tab_runtime:
    st.json(report.get("runtime"))

with tab_approval:
    st.json(report.get("approval"))

with tab_audit:
    st.json(report.get("audit"))

with tab_report:
    if st.button("Reconstruir relatorio"):
        report = dashboard.build_report()
        st.success("Relatorio reconstruido.")
    st.json(report)
