# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.executor_package_builder import build_executor_packages


st.set_page_config(
    page_title="K-Atlas Executor Package Builder",
    layout="wide",
)

st.title("K-Atlas Executor Package Builder")
st.caption("Transforma decisoes aprovadas em pacotes de execucao futura supervisionada. Nao executa acao real.")

stage = st.number_input("Checkpoint", min_value=1, value=64, step=1)

if st.button("Gerar pacotes de execucao futura", type="primary"):
    st.session_state["epb_result"] = build_executor_packages(stage=int(stage))

if "epb_result" not in st.session_state:
    st.session_state["epb_result"] = build_executor_packages(stage=int(stage))

result = st.session_state["epb_result"]
summary = result["summary"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Decisoes lidas", summary["human_decisions_read"])
col2.metric("Aprovadas", summary["approved_decisions"])
col3.metric("Pacotes criados", summary["executor_packages_built"])
col4.metric("Ignoradas", summary["denied_decisions_skipped"] + summary["adjustment_decisions_skipped"] + summary["unknown_decisions_skipped"])

st.info(
    "Governanca ativa: nenhum pacote executa acao real. "
    "Sem API externa, sem publicacao, sem deploy, sem envio automatico e sem token em texto puro."
)

packages = result["executor_packages"]

if not packages:
    st.warning("Nenhuma decisao aprovada encontrada para transformar em pacote de execucao futura.")
    st.stop()

for package in packages:
    with st.expander(f"{package['executor_package_id']} | {package['source_package_id']}", expanded=False):
        st.write("Status:", package["package_status"])
        st.write("Modo:", package["execution_mode"])
        st.write("Proxima acao:", package["next_required_action"])
        st.write("Operador:", package["human_operator"])
        st.write("Justificativa:", package["human_reason"])
        st.write("Artefatos:", package["artifact_paths"])

        st.write("Tarefas futuras:")
        for task in package["tasks"]:
            st.write(f"- {task['task_id']} | {task['task_type']} | {task['execution_status']}")

st.divider()
st.caption(
    "Arquivos principais: live/executor_package_builder/executor_package_queue.json | "
    "memory/executor_package_builder/events.jsonl | reports/executor_packages/"
)
