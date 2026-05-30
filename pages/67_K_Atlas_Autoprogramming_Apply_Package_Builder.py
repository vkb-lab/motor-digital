from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autoprogramming_apply_package_builder.builder import AutoprogrammingApplyPackageBuilder


st.set_page_config(page_title="K-Atlas Apply Package Builder", layout="wide")

st.title("K-Atlas Autoprogramming Apply Package Builder")
st.caption("Transforma propostas aprovadas em pacotes de aplicacao futura. Nao aplica nada.")

builder = AutoprogrammingApplyPackageBuilder()
summary = builder.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Reviews", metrics.get("reviews_total", 0))

with col2:
    st.metric("Pacotes", metrics.get("package_queue_total", 0))

with col3:
    st.metric("Aguardando gate", metrics.get("waiting_execution_gate_validation", 0))

with col4:
    st.metric("Execucao real", str(metrics.get("real_execution_enabled", False)))

st.divider()

tab_build, tab_packages, tab_report = st.tabs(["Gerar pacotes", "Pacotes", "Relatorio"])

with tab_build:
    st.write("Gera pacotes somente a partir de reviews aprovados para apply package.")
    if st.button("Construir pacotes de aplicacao futura", type="primary"):
        result = builder.build_apply_packages({
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
        })
        st.success("Processo concluido. Nenhuma aplicacao real foi feita.")
        st.json(result)

with tab_packages:
    current = builder.summary()
    packages = current.get("packages", [])

    if not packages:
        st.info("Nenhum pacote encontrado.")
    else:
        for item in packages:
            title = f"{item.get('checkpoint')} | {item.get('status')} | {item.get('objective')}"
            with st.expander(title):
                st.json(item)

with tab_report:
    st.json(builder.save_report())
