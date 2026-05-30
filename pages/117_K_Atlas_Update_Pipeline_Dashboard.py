from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.update_pipeline_dashboard.dashboard import UpdatePipelineDashboard

st.set_page_config(page_title="K-Atlas Update Pipeline Dashboard", layout="wide")
st.title("K-Atlas Update Pipeline Dashboard")
st.caption("Painel do pipeline de updates 113-117.")

dashboard = UpdatePipelineDashboard()\nst.json(dashboard.build_report())
