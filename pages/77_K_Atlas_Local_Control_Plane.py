from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_control_plane.control_plane import KAtlasLocalControlPlane


st.set_page_config(page_title="K-Atlas Local Control Plane", layout="wide")

st.title("K-Atlas Local Control Plane")
st.caption("Sistema operacional local do K-Atlas: observa, recomenda e prepara autonomia assistida.")

control_plane = KAtlasLocalControlPlane()
report = control_plane.build_report({"mode": "observe"})
state = report.get("state", {})
summary = report.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Control Plane", str(summary.get("control_plane_ready", False)))

with col2:
    st.metric("Modulos", f"{summary.get('modules_ready', 0)}/{summary.get('modules_total', 0)}")

with col3:
    st.metric("Acoes pendentes", summary.get("pending_actions", 0))

with col4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()

tab_os, tab_modules, tab_queues, tab_network, tab_report = st.tabs([
    "OS",
    "Modulos",
    "Filas",
    "Rede local",
    "Relatorio",
])

with tab_os:
    st.subheader("Acoes recomendadas")
    for action in state.get("pending_actions", []):
        with st.expander(f"{action.get('priority')} | {action.get('action')}"):
            st.write(action.get("human_instruction"))
            st.json(action)

    st.subheader("Guardrails")
    for item in report.get("guardrails", []):
        st.write(f"- {item}")

with tab_modules:
    st.subheader("Camada operacional")
    for item in state.get("modules", []):
        with st.expander(f"{item.get('checkpoint')} | {item.get('name')} | {item.get('status')}"):
            st.write(item.get("role"))
            st.json(item)

with tab_queues:
    st.subheader("Estado das filas")
    st.json(state.get("queues", {}))

with tab_network:
    st.subheader("Readiness LAN / remoto assistido")
    st.json(state.get("lan_readiness", {}))
    st.subheader("Portas locais conhecidas")
    st.json(state.get("cockpit", {}))

with tab_report:
    st.subheader("Relatorio completo")
    if st.button("Reconstruir Control Plane", type="primary"):
        report = control_plane.build_report({"mode": "recommend"})
        st.success("Control Plane reconstruido.")
    st.json(report)
