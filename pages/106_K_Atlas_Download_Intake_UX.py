from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.download_intake_ux.manager import DownloadIntakeUX


st.set_page_config(page_title="K-Atlas Download Intake UX", layout="wide")

st.title("K-Atlas Download Intake UX")
st.caption("Fluxo otimizado: baixar arquivo, voltar ao PowerShell principal e rodar sempre o mesmo comando.")

manager = DownloadIntakeUX()
report = manager.summary()
summary = report.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Checkpoint", report.get("checkpoint"))

with col2:
    st.metric("Status", report.get("status"))

with col3:
    st.metric("Executados", summary.get("executed_installers", 0))

with col4:
    st.metric("Janelas extras", str(summary.get("extra_windows_required", False)))

st.divider()

st.subheader("Comando fixo")

st.code(report.get("fixed_command", ""), language="powershell")

tab_fluxo, tab_download, tab_report = st.tabs(["Fluxo", "Ultimo download", "Relatorio"])

with tab_fluxo:
    st.markdown(
        """
1. Baixe o proximo arquivo `K_ATLAS_*.ps1` no chat.
2. Volte para o PowerShell principal.
3. Rode sempre o mesmo comando fixo.
4. O K-Atlas detecta o instalador novo e executa.
"""
    )

with tab_download:
    st.json(report.get("latest_download"))

with tab_report:
    st.json(report)
