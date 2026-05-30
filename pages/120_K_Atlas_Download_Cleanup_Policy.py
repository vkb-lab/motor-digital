from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.download_cleanup_policy.policy import DownloadCleanupPolicy

st.set_page_config(page_title="K-Atlas Download Cleanup", layout="wide")
st.title("K-Atlas Download Cleanup Policy")

policy = DownloadCleanupPolicy()
report = policy.build_report()
st.metric("Installers em Downloads", report.get("summary", {}).get("download_installers_found", 0))
st.json(report)
