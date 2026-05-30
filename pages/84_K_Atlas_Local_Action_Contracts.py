from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_action_contracts.contracts import LocalActionContractRegistry

st.set_page_config(page_title="K-Atlas Action Contracts", layout="wide")
st.title("K-Atlas Local Action Contract Registry")
st.caption("Contratos seguros de acao local. Nenhuma execucao automatica.")

registry = LocalActionContractRegistry()

if st.button("Reconstruir contratos", type="primary"):
    st.json(registry.build_contracts())

st.json(registry.summary())
