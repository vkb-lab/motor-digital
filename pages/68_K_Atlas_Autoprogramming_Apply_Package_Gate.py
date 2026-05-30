from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autoprogramming_apply_package_gate.gate import AutoprogrammingApplyPackageGate


st.set_page_config(page_title="K-Atlas Apply Package Gate", layout="wide")

st.title("K-Atlas Autoprogramming Apply Package Gate")
st.caption("Valida pacotes de aplicacao antes de qualquer escrita real.")

gate = AutoprogrammingApplyPackageGate()
summary = gate.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Pacotes", metrics.get("packages_total", 0))

with col2:
    st.metric("Gate queue", metrics.get("gate_queue_total", 0))

with col3:
    st.metric("Aguardando humano", metrics.get("waiting_human_apply_approval", 0))

with col4:
    st.metric("Execucao real", str(metrics.get("real_execution_enabled", False)))

st.divider()

tab_build, tab_items, tab_report = st.tabs(["Validar pacotes", "Fila do gate", "Relatorio"])

with tab_build:
    st.write("Cria validações para pacotes aguardando Execution Gate.")
    if st.button("Construir fila do gate", type="primary"):
        result = gate.build_gate_queue()
        st.success("Gate executado. Nenhuma aplicacao real foi feita.")
        st.json(result)

with tab_items:
    current = gate.summary()
    items = current.get("gate_items", [])

    if not items:
        st.info("Nenhum item no gate.")
    else:
        for item in items:
            title = f"{item.get('checkpoint')} | {item.get('status')} | {item.get('objective')}"
            with st.expander(title):
                st.json(item)

with tab_report:
    st.json(gate.save_report())
