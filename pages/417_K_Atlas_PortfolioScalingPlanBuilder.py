from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.portfolio_scaling_plan_builder.core import KAtlasComponent


st.set_page_config(page_title="K-Atlas Portfolio Scaling Plan Builder", layout="wide")

component = KAtlasComponent()
summary = component.summary()

st.title("K-Atlas Portfolio Scaling Plan Builder")
st.caption("Checkpoint 417 - gerado pelo K-Atlas Local Batch Factory.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Checkpoint", summary.get("checkpoint"))

with col2:
    st.metric("Status", summary.get("status"))

with col3:
    st.metric("Execucao real", str(summary.get("real_execution_enabled")))

with col4:
    st.metric("Side effects", summary.get("external_side_effects"))

st.divider()

tab_summary, tab_guardrails = st.tabs(["Resumo", "Guardrails"])

with tab_summary:
    st.json(summary)

with tab_guardrails:
    for item in summary.get("guardrails", []):
        st.write("- " + item)
