from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_api_audit_ledger.ledger import LocalApiAuditLedger


st.set_page_config(page_title="K-Atlas API Audit Ledger", layout="wide")
st.title("K-Atlas API Audit Ledger")
st.caption("Registro auditavel de eventos da API local.")

ledger = LocalApiAuditLedger()

if st.button("Registrar evento demo"):
    st.json(ledger.append("streamlit.demo_event", {"source": "page_92"}))

st.subheader("Ledger")
st.json(ledger.summary())
