from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_os_brain_governance.brain import LocalOSBrainGovernance


st.set_page_config(page_title="K-Atlas Brain Governance", layout="wide")

st.title("K-Atlas Local OS Brain Governance")
st.caption("Agentes obedecem ao cerebro. Cerebro obedece a politica. Humano aprova acoes sensiveis.")

brain = LocalOSBrainGovernance()
report = brain.build_report()
summary = report.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Decisoes", summary.get("decisions_total", 0))

with col2:
    st.metric("Safe approved", summary.get("safe_approved", 0))

with col3:
    st.metric("Humano requerido", summary.get("requires_human_approval", 0))

with col4:
    st.metric("Bloqueadas", summary.get("blocked", 0))

st.divider()

tab_decide, tab_matrix, tab_report = st.tabs(["Decisao", "Permissoes", "Relatorio"])

with tab_decide:
    st.subheader("Criar decisao do cerebro")
    agent = st.selectbox("Agente", ["operator", "mission_generator", "execution_agent", "remote_assist_agent"])
    action = st.selectbox(
        "Acao",
        [
            "observe_status",
            "generate_report",
            "create_local_mission",
            "queue_for_human_approval",
            "run_dry_run",
            "apply_local_change",
            "rollback_local_change",
            "start_local_service",
            "open_lan_access",
            "control_mouse",
            "external_api_call",
            "deploy_external",
        ],
    )

    if st.button("Avaliar pelo cerebro", type="primary"):
        decision = brain.decide({
            "agent": agent,
            "action": action,
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        })
        feedback = brain.route_feedback(decision)
        st.json({"decision": decision, "feedback": feedback})

with tab_matrix:
    st.subheader("Agent Permission Matrix")
    st.json(brain.save_permission_matrix())

with tab_report:
    st.subheader("Governance report")
    st.json(brain.build_report())
