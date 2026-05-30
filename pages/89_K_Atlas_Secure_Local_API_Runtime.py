from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.secure_local_api_runtime.runtime import SecureLocalApiRuntime


st.set_page_config(page_title="K-Atlas Secure Local API Runtime", layout="wide")
st.title("K-Atlas Secure Local API Runtime")
st.caption("Runtime API local seguro. Somente localhost por padrao.")

runtime = SecureLocalApiRuntime()
status = runtime.status()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Status", status.get("status"))
with col2:
    st.metric("Execucao real", str(status.get("real_execution_enabled")))
with col3:
    st.metric("Side effects", status.get("external_side_effects"))

st.divider()

if st.button("Reconstruir configuracao localhost"):
    st.json(runtime.build_config())

st.subheader("Status")
st.json(status)
