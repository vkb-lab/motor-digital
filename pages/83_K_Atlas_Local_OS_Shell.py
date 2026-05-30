from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_os_shell_dashboard.shell import LocalOSShellDashboard

st.set_page_config(page_title="K-Atlas Local OS Shell", layout="wide")
st.title("K-Atlas Local OS Shell")
st.caption("Camada visual unificada do K-Atlas Local OS. Observa, organiza e exige aprovacao humana.")

shell = LocalOSShellDashboard()
report = shell.build_report()
summary = report.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Componentes", summary.get("components_total", 0))
with c2:
    st.metric("Operacionais", summary.get("components_operational", 0))
with c3:
    st.metric("Local OS ready", str(summary.get("local_os_ready", False)))
with c4:
    st.metric("Controle remoto", str(summary.get("remote_control_enabled", False)))

st.divider()
tab_components, tab_network, tab_approval, tab_report = st.tabs(["Componentes", "Rede", "Aprovacoes", "Relatorio"])

with tab_components:
    for item in report.get("components", []):
        with st.expander(f"{item.get('checkpoint')} | {item.get('name')} | {item.get('status')}"):
            st.json(item)

with tab_network:
    st.subheader("LAN")
    st.json(report.get("lan_cockpit_access"))
    st.subheader("Remote tunnel gate")
    st.json(report.get("remote_tunnel_gate"))

with tab_approval:
    st.json(report.get("operator_approval_console"))

with tab_report:
    st.json(report)
