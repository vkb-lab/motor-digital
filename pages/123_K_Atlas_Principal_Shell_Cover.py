from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.principal_shell_cover.cover import PrincipalShellCover


st.set_page_config(page_title="K-Atlas Principal Shell", layout="wide")

st.title("K-Atlas Principal Shell Cover")
st.caption("Home operacional do PowerShell principal do K-Atlas Local OS.")

cover = PrincipalShellCover()
status = cover.build_status()
summary = status.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", status.get("status"))

with col2:
    st.metric("Modules ready", f"{summary.get('modules_ready')}/{summary.get('modules_total')}")

with col3:
    st.metric("Principal ready", str(summary.get("principal_shell_ready")))

with col4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled")))

st.divider()

tab_home, tab_modules, tab_commands, tab_report = st.tabs(["Home", "Modulos", "Atalhos", "Relatorio"])

with tab_home:
    st.code(cover.render_text(), language="text")

with tab_modules:
    for item in status.get("modules", []):
        st.write(f"{item.get('name')} - {item.get('exists')} - {item.get('path')}")

with tab_commands:
    for item in status.get("quick_commands", []):
        st.code(item.get("command"), language="powershell")

with tab_report:
    st.json(status)
