from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.one_click_launcher.launcher import OneClickLauncher

st.set_page_config(page_title="K-Atlas One-Click Launcher", layout="wide")
st.title("K-Atlas One-Click Launcher")
st.caption("Checkpoint 103 - comandos prontos para abrir cockpits.")

plan = OneClickLauncher().build_launch_plan()
summary = plan.get("summary", {})

st.metric("Targets prontos", summary.get("launch_targets_ready", 0))
st.warning("Este painel mostra comandos. A execucao permanece sob controle humano.")

for target in plan.get("targets", []):
    with st.expander(target.get("name", "target")):
        st.code(target.get("command", ""), language="powershell")
        st.json(target)
