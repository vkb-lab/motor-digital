from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_api_auth_policy.policy import validate_local_api_runtime_request


st.set_page_config(page_title="K-Atlas Local API Auth Policy", layout="wide")
st.title("K-Atlas Local API Auth Policy")
st.caption("Politica de acesso local: bloqueia porta publica e execucao automatica.")

host = st.selectbox("Bind host", ["127.0.0.1", "localhost", "0.0.0.0"], index=0)
port = st.number_input("Porta", min_value=1, max_value=65535, value=8787)

result = validate_local_api_runtime_request({
    "bind_host": host,
    "port": int(port),
    "auto_execute": False,
    "real_execution_enabled": False,
    "external_public_access": False,
    "remote_control_enabled": False,
})

st.json(result)
