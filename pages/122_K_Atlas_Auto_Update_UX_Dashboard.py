from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.auto_update_ux_dashboard.dashboard import AutoUpdateUXDashboard

st.set_page_config(page_title="K-Atlas Auto Update UX", layout="wide")
st.title("K-Atlas Auto Update UX Dashboard")
st.caption("Fluxo: download -> watcher invisivel -> popup -> clipboard ok/erro -> retorno ao chat.")

dashboard = AutoUpdateUXDashboard()
report = dashboard.build_report()
summary = report.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Status", report.get("status"))
c2.metric("UX", "silent")
c3.metric("Execucao real", "False")
c4.metric("Side effects", "reports")

st.divider()
st.json(report)
