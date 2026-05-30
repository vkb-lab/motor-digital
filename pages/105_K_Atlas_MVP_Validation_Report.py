from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.mvp_validation_report.validation import MVPValidationReport

st.set_page_config(page_title="K-Atlas MVP Validation", layout="wide")
st.title("K-Atlas MVP Validation Report")
st.caption("Checkpoint 105 - relatorio de validacao do MVP Local OS.")

report = MVPValidationReport().build_report()
summary = report.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Score", summary.get("validation_score", 0))
c2.metric("Gates", summary.get("gates_total", 0))
c3.metric("Passou", summary.get("gates_passed", 0))
c4.metric("Release candidate", str(summary.get("release_candidate", False)))

st.divider()
st.subheader("Gates")
st.dataframe(report.get("gates", []), use_container_width=True)

with st.expander("Relatorio completo"):
    st.json(report)
