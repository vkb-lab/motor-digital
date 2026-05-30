from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.silent_update_status_center.status_center import SilentUpdateStatusCenter

st.set_page_config(page_title="K-Atlas Silent Update Status", layout="wide")
st.title("K-Atlas Silent Update Status Center")

center = SilentUpdateStatusCenter()
report = center.build_report()

st.metric("Status", report.get("status"))
st.metric("Eventos", report.get("summary", {}).get("events_loaded", 0))
st.json(report)
