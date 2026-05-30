from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.mission_pack_bridge.bridge import MissionPackBridge


st.set_page_config(page_title="K-Atlas Mission Pack Bridge", layout="wide")

st.title("K-Atlas Mission Pack Bridge")
st.caption("Converte mission packs em local missions instalaveis pelo Local Mission Installer.")

bridge = MissionPackBridge()
summary = bridge.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Local missions", metrics.get("generated_local_missions_total", 0))

with col2:
    st.metric("Latest exists", str(metrics.get("latest_local_mission_exists", False)))

with col3:
    st.metric("Execucao real", "False")

with col4:
    st.metric("Side effects", metrics.get("external_side_effects", "none"))

st.divider()

tab_bridge, tab_latest, tab_report = st.tabs(["Converter latest pack", "Ultima local mission", "Resumo"])

with tab_bridge:
    st.write("Converte live/mission_pack_generator/latest_mission_pack.json para .kmission.json.")
    if st.button("Converter latest mission pack", type="primary"):
        result = bridge.bridge_latest()
        if result.get("ok"):
            st.success("Local mission gerada. Nenhuma instalacao foi feita.")
        else:
            st.error("Conversao bloqueada ou source pack ausente.")
        st.json(result)

with tab_latest:
    st.json(bridge.summary().get("latest_local_mission"))

with tab_report:
    st.json(bridge.summary())
