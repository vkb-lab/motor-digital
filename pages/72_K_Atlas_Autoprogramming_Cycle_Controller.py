from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autoprogramming_cycle_controller.controller import AutoprogrammingCycleController

st.set_page_config(page_title="K-Atlas Cycle Controller", layout="wide")
st.title("K-Atlas Autoprogramming Cycle Controller")
st.caption("Controlador operacional do ciclo assistido. Recomenda, mas nao executa.")

controller = AutoprogrammingCycleController()
summary = controller.summary()
metrics = summary.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cycle ready", str(metrics.get("cycle_ready", False)))
c2.metric("Decisoes", metrics.get("decision_queue_total", 0))
c3.metric("Execucao real", str(metrics.get("real_execution_enabled", False)))
c4.metric("Side effects", metrics.get("external_side_effects", "none"))

tab1, tab2, tab3 = st.tabs(["Controlador", "Estado", "Ultima decisao"])

with tab1:
    mode = st.selectbox("Modo", ["recommend", "observe", "plan"], index=0)
    if st.button("Gerar decisao do ciclo", type="primary"):
        st.json(controller.build_decision({"mode": mode, "auto_execute": False, "real_execution_enabled": False, "external_api_enabled": False, "auto_publish": False, "auto_send": False, "auto_deploy": False}))

with tab2:
    st.json(summary.get("state", {}))

with tab3:
    st.json(summary.get("latest_decision"))
