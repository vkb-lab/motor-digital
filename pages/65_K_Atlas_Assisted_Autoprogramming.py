from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.assisted_autoprogramming.kernel import AssistedAutoprogrammingKernel
from k_atlas.core.assisted_autoprogramming.policy import validate_autoprog_request


st.set_page_config(page_title="K-Atlas Autoprogramacao Assistida", layout="wide")

st.title("K-Atlas Autoprogramacao Assistida")
st.caption("Proposta, validacao e pacote antes de qualquer alteracao real.")

kernel = AssistedAutoprogrammingKernel()
summary = kernel.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Propostas", metrics.get("proposal_queue_total", 0))

with col2:
    st.metric("Pacotes", metrics.get("package_queue_total", 0))

with col3:
    st.metric("Aguardando revisao", metrics.get("waiting_human_review", 0))

with col4:
    st.metric("Execucao real", str(metrics.get("real_execution_enabled", False)))

st.divider()

tab_new, tab_queue, tab_report = st.tabs(["Nova proposta", "Fila", "Relatorio"])

with tab_new:
    checkpoint = st.text_input("Checkpoint", value="65")
    action = st.selectbox("Acao", [
        "create_module",
        "create_streamlit_page",
        "create_smoke_test",
        "create_ops_script",
        "create_readme",
        "update_gitignore",
        "create_report",
    ])

    objective = st.text_area(
        "Objetivo da autoprogramacao assistida",
        value="Criar modulo seguro e auditavel para evolucao do K-Atlas.",
        height=160,
    )

    payload = {
        "checkpoint": checkpoint,
        "action": action,
        "objective": objective,
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "browser_automation": False,
        "mouse_automation": False,
    }

    validation = validate_autoprog_request(payload)

    if validation["ok"]:
        st.success("Payload permitido pela politica.")
    else:
        st.error("Payload bloqueado pela politica.")

    st.json(validation)

    if st.button("Criar proposta supervisionada", type="primary"):
        result = kernel.create_proposal(payload)
        if result["ok"]:
            st.success("Proposta criada. Nenhuma execucao real foi feita.")
        else:
            st.error("Proposta bloqueada.")
        st.json(result)

with tab_queue:
    current = kernel.summary()
    st.subheader("Propostas")
    for item in current.get("proposals", []):
        with st.expander(f"{item.get('checkpoint')} | {item.get('status')} | {item.get('objective')}"):
            st.json(item)

    st.subheader("Pacotes")
    for item in current.get("packages", []):
        with st.expander(f"{item.get('checkpoint')} | {item.get('status')} | {item.get('objective')}"):
            st.json(item)

with tab_report:
    st.json(kernel.save_report())
