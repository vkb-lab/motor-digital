from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.safe_task_planner.planner import SafeTaskPlanner

st.set_page_config(page_title="K-Atlas Safe Task Planner", layout="wide")
st.title("K-Atlas Safe Task Planner")
st.caption("Cria planos seguros sem execucao automatica.")

planner = SafeTaskPlanner()
goal = st.text_input("Objetivo", value="prepare_next_safe_local_mission")
if st.button("Criar plano seguro", type="primary"):
    st.json(planner.create_plan(goal))
st.divider()
st.json(planner.summary())
