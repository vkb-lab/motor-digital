from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.startup_manager.manager import StartupManager

st.set_page_config(page_title="K-Atlas Startup Manager", layout="wide")
st.title("K-Atlas Startup Manager")
st.caption("Checkpoint 102 - alvos de abertura supervisionada.")

manager = StartupManager()
config = manager.build_config()
summary = config.get("summary", {})

c1, c2, c3 = st.columns(3)
c1.metric("Targets", summary.get("targets_total", 0))
c2.metric("Prontos", summary.get("targets_ready", 0))
c3.metric("Autostart", str(summary.get("autostart_enabled", False)))

st.divider()
for target in config.get("targets", []):
    with st.expander(f"{target.get('name')} | {target.get('status')}"):
        st.code(target.get("command", ""), language="powershell")
        st.json(target)
