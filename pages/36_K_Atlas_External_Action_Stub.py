from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.external_action_stub.stub import ExternalActionExecutionStub
from k_atlas.core.publish_approval_gate.gate import SecurePublishApprovalGate


REPORT = Path("reports/external_action_stub/latest_external_action_stub.json")

st.set_page_config(page_title="K-Atlas External Action Stub", layout="wide")

st.title("K-Atlas External Action Execution Stub")
st.caption("Simula execução de ações aprovadas. Nenhuma API externa é chamada.")

gate = SecurePublishApprovalGate()
stub = ExternalActionExecutionStub(approval_gate=gate)

latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Aprovados", len(gate.approved()))

with col2:
    st.metric("Executados stub", latest.get("executed_stubs", 0) if latest else 0)

with col3:
    st.metric("Real execution", str(latest.get("real_execution_enabled", False) if latest else False))

with col4:
    st.metric("Side effects", latest.get("external_side_effects", "none") if latest else "none")

st.divider()

tab_run, tab_results, tab_approved, tab_report = st.tabs(["Executar stubs", "Resultados", "Aprovados", "Relatório"])

with tab_run:
    st.warning("Esta etapa não chama Instagram, WhatsApp, Render, GitHub ou qualquer API externa.")

    limit = st.number_input("Limite de pedidos aprovados", min_value=1, max_value=50, value=10)

    if st.button("Executar stubs aprovados", type="primary"):
        result = stub.execute_approved_stubs(limit=int(limit))
        st.success("Stubs executados sem efeitos externos.")
        st.json(result)

with tab_results:
    if not latest:
        st.info("Nenhum stub executado ainda.")
    else:
        for item in latest.get("results", []):
            with st.expander(f"{item.get('request_id')} | {item.get('status')}"):
                st.json(item)

with tab_approved:
    approved = gate.approved()
    if not approved:
        st.info("Nenhum pedido aprovado aguardando stub.")
    else:
        for item in approved:
            with st.expander(f"{item.get('request_id')} | {item.get('payload', {}).get('title')}"):
                st.json(item)

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
