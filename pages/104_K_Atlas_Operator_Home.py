from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.operator_home.home import OperatorHome

st.set_page_config(page_title="K-Atlas Operator Home", layout="wide")
st.title("K-Atlas Operator Home")
st.caption("Checkpoint 104 - pagina inicial operacional do K-Atlas Local OS.")

home = OperatorHome().build_home()
summary = home.get("summary", {})

c1, c2, c3 = st.columns(3)
c1.metric("Health", summary.get("health_readiness", 0))
c2.metric("Launch targets", summary.get("launch_targets_ready", 0))
c3.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()
st.subheader("Acoes prontas")
for target in home.get("launch_targets", []):
    with st.expander(target.get("name", "target")):
        st.code(target.get("command", ""), language="powershell")

st.subheader("Resumo")
st.json(home)
