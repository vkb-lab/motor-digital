from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_os_release_capsule.capsule import LocalOSReleaseCapsule


st.set_page_config(page_title="K-Atlas Local OS Release Capsule", layout="wide")

st.title("K-Atlas Local OS Release Capsule")
st.caption("Checkpoint 100 - capsula de entrega do MVP Local OS supervisionado.")

capsule_runner = LocalOSReleaseCapsule()
capsule = capsule_runner.build_capsule()
summary = capsule.get("readiness_summary", {})
next_phase = capsule.get("next_phase", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Versao", capsule.get("version"))

with col2:
    st.metric("Status", capsule.get("status"))

with col3:
    st.metric("Readiness", summary.get("readiness_score", 0))

with col4:
    st.metric("Execucao real", str(capsule.get("real_execution_enabled", False)))

st.divider()

tab_scope, tab_guardrails, tab_next, tab_report = st.tabs(["Escopo", "Guardrails", "Proxima fase", "Relatorio"])

with tab_scope:
    st.subheader("Escopo da entrega")
    for item in capsule.get("release_scope", []):
        st.write(f"- {item}")

with tab_guardrails:
    st.subheader("Governanca")
    for item in capsule.get("release_guardrails", []):
        st.write(f"- {item}")

with tab_next:
    st.subheader(next_phase.get("name"))
    st.write(next_phase.get("goal"))
    st.info(next_phase.get("suggested_start"))

with tab_report:
    st.json(capsule)
