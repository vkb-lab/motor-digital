from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.secure_local_api_readiness.api import SecureLocalApiReadiness

st.set_page_config(page_title="K-Atlas Secure Local API", layout="wide")
st.title("K-Atlas Secure Local API Readiness")
st.caption("Prepara API local segura. Nao abre servidor e nao altera firewall.")

api = SecureLocalApiReadiness()
report = api.build_report({"mode": "readiness", "bind_address": "127.0.0.1"})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Status", report.get("status"))
with c2:
    st.metric("Local IP", report.get("network", {}).get("local_ip"))
with c3:
    st.metric("Bind seguro", report.get("network", {}).get("default_safe_bind"))
with c4:
    st.metric("Execucao real", str(report.get("real_execution_enabled")))

st.divider()
st.json(report)
