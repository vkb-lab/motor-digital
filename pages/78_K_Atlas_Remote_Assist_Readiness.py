from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.remote_assist_readiness.readiness import RemoteAssistReadiness


st.set_page_config(page_title="K-Atlas Remote Assist Readiness", layout="wide")

st.title("K-Atlas Remote Assist Readiness")
st.caption("Preparacao segura para LAN/remoto assistido. Nao controla mouse, nao abre porta publica.")

readiness = RemoteAssistReadiness()
report = readiness.build_readiness()
summary = report.get("summary", {})
machine = report.get("machine", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("LAN IPv4", str(summary.get("lan_ipv4_detected", False)))

with col2:
    st.metric("Streamlit local", str(summary.get("streamlit_local_detected", False)))

with col3:
    st.metric("Controle remoto", str(summary.get("remote_control_enabled", False)))

with col4:
    st.metric("Exposicao publica", str(summary.get("public_exposure_enabled", False)))

st.divider()

tab_ready, tab_ports, tab_policy, tab_report = st.tabs([
    "Readiness",
    "Portas locais",
    "Politica",
    "Relatorio",
])

with tab_ready:
    st.subheader("Maquina local")
    st.json(machine)

    st.subheader("Modelo de acesso assistido")
    st.json(report.get("remote_assist_model", {}))

with tab_ports:
    st.subheader("Portas locais verificadas")
    st.dataframe(report.get("ports", []), use_container_width=True)

with tab_policy:
    st.subheader("Guardrails")
    for item in report.get("guardrails", []):
        st.write(f"- {item}")

    st.subheader("Policy")
    st.json(report.get("policy", {}))

with tab_report:
    if st.button("Reconstruir readiness", type="primary"):
        report = readiness.build_readiness()
        st.success("Readiness reconstruido.")
    st.json(report)
