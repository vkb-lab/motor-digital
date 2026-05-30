from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_action_router.router import LocalActionRouter

st.set_page_config(page_title="K-Atlas Action Router", layout="wide")
st.title("K-Atlas Local Action Router")
st.caption("Roteia acoes locais aprovadas. Nao executa.")

router = LocalActionRouter()
action_type = st.selectbox("Action type", ["run_mission_pipeline", "install_local_mission", "create_local_report"])

if st.button("Criar rota segura", type="primary"):
    result = router.route({
        "action_type": action_type,
        "human_approved": True,
        "auto_execute": False,
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "browser_automation": False,
        "mouse_automation": False,
        "remote_control_enabled": False,
    })
    st.json(result)

st.divider()
st.json(router.summary())
