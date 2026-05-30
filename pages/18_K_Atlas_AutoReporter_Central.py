from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autoreporter.report_builder import AutoReporterCentral
from k_atlas.core.autoreporter.snapshot import build_system_snapshot


REPORT_JSON = Path("reports/autoreporter/k_atlas_central_report.json")
REPORT_MD = Path("reports/autoreporter/k_atlas_central_report.md")

st.set_page_config(page_title="K-Atlas AutoReporter Central", layout="wide")

st.title("K-Atlas AutoReporter Central")
st.caption("Relatório central do estado operacional do K-Atlas OS.")

snapshot = build_system_snapshot()
metrics = snapshot["metrics"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Módulos OK", f"{metrics['modules_ok']}/{metrics['modules_total']}")

with col2:
    st.metric("Páginas", metrics["streamlit_pages"])

with col3:
    st.metric("Eventos", metrics["control_plane_events"])

with col4:
    st.metric("Fila supervisor", metrics["supervisor_queue_items"])

st.divider()

tab_generate, tab_snapshot, tab_report = st.tabs(["Gerar relatório", "Snapshot", "Relatório Markdown"])

with tab_generate:
    st.subheader("Gerar relatório central")

    if st.button("Gerar AutoReport", type="primary"):
        result = AutoReporterCentral().generate()
        st.success("Relatório gerado.")
        st.json(result)

with tab_snapshot:
    st.subheader("Snapshot atual")
    st.json(snapshot)

with tab_report:
    st.subheader("Relatório salvo")

    if REPORT_MD.exists():
        st.markdown(REPORT_MD.read_text(encoding="utf-8"))
    else:
        st.info("Nenhum relatório Markdown salvo ainda. Gere o relatório primeiro.")
