from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.operator_approval_console.console import OperatorApprovalConsole

st.set_page_config(page_title="K-Atlas Approval Console", layout="wide")
st.title("K-Atlas Operator Approval Console")
st.caption("Fila de aprovacao humana. Aprova decisoes, mas nao executa automaticamente.")

console = OperatorApprovalConsole()
summary = console.summary()
metrics = summary.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Fila", metrics.get("approval_queue_total", 0))
with c2:
    st.metric("Aguardando", metrics.get("waiting_operator_decision", 0))
with c3:
    st.metric("Aprovadas", metrics.get("approved_by_operator", 0))
with c4:
    st.metric("Auto execucao", str(metrics.get("automatic_execution_allowed", False)))

st.divider()
tab_new, tab_queue = st.tabs(["Nova solicitacao", "Fila"])

with tab_new:
    title = st.text_input("Titulo", value="Solicitacao manual")
    action_type = st.selectbox("Tipo", ["mission_install", "mission_pipeline_run", "dashboard_open", "local_api_readiness", "lan_readiness", "remote_tunnel_readiness", "manual_checkpoint"])
    description = st.text_area("Descricao", value="Aguardando aprovacao humana.")
    if st.button("Criar solicitacao"):
        st.json(console.create_request({"action_type": action_type, "title": title, "description": description, "auto_execute": False, "real_execution_enabled": False}))

with tab_queue:
    for item in console.load_queue():
        with st.expander(f"{item.get('status')} | {item.get('request', {}).get('title')}"):
            st.json(item)
