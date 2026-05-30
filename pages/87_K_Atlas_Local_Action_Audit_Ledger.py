from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_action_audit_ledger.ledger import LocalActionAuditLedger

st.set_page_config(page_title="K-Atlas Audit Ledger", layout="wide")
st.title("K-Atlas Local Action Audit Ledger")
st.caption("Auditoria local de rotas e fila de execucao.")

ledger = LocalActionAuditLedger()

if st.button("Reconstruir auditoria", type="primary"):
    st.json(ledger.build_report())
else:
    st.json(ledger.build_report())
