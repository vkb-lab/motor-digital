from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_api_approval_bridge.bridge import LocalApiApprovalBridge


st.set_page_config(page_title="K-Atlas API Approval Bridge", layout="wide")
st.title("K-Atlas API Approval Bridge")
st.caption("Fila de solicitacoes vindas da API local. Nao executa automaticamente.")

bridge = LocalApiApprovalBridge()

if st.button("Criar solicitacao demo"):
    item = bridge.create_request({"source": "streamlit_demo", "intent": "demo_no_op"})
    st.success("Solicitacao criada. Nenhuma execucao real foi feita.")
    st.json(item)

st.subheader("Resumo")
st.json(bridge.summary())
