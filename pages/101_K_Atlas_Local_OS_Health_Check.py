from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_os_health_check.health import LocalOSHealthCheck

st.set_page_config(page_title="K-Atlas Health Check", layout="wide")
st.title("K-Atlas Local OS Health Check")
st.caption("Checkpoint 101 - verificacao geral do MVP local OS.")

report = LocalOSHealthCheck().collect()
summary = report.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Componentes", summary.get("components_total", 0))
c2.metric("Prontos", summary.get("components_ready", 0))
c3.metric("Readiness", summary.get("readiness", 0))
c4.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()
st.subheader("Componentes")
st.dataframe(report.get("components", []), use_container_width=True)

with st.expander("Relatorio"):
    st.json(report)
