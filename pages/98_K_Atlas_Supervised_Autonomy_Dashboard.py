from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.supervised_autonomy_dashboard.dashboard import SupervisedAutonomyDashboard

st.set_page_config(page_title="K-Atlas Supervised Autonomy", layout="wide")
st.title("K-Atlas Supervised Autonomy Dashboard")
st.caption("Painel da camada de autonomia supervisionada 94-98.")

dashboard = SupervisedAutonomyDashboard()
report = dashboard.build_report()
summary = report.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Policy", summary.get("policy_status"))
with c2:
    st.metric("Queue", summary.get("autonomy_queue_total", 0))
with c3:
    st.metric("Violations", summary.get("violations_total", 0))
with c4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()
st.json(report)
