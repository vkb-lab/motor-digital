# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.human_decision_center import ALLOWED_DECISIONS, build_queue, record_decision


st.set_page_config(
    page_title="K-Atlas Decision Center",
    layout="wide",
)

st.title("K-Atlas Human Decision Center")
st.caption("Aprovacao humana local para pacotes do Planning Approval Packager. Sem publicacao automatica.")

stage = st.number_input("Etapa operacional", min_value=1, value=63, step=1)

queue = build_queue(stage=int(stage), emit_event=True)
summary = queue["summary"]

col_total, col_pending, col_decided = st.columns(3)

col_total.metric("Pacotes", summary["total_packages"])
col_pending.metric("Pendentes", summary["pending_decisions"])
col_decided.metric("Decididos", summary["decided_packages"])

st.info(
    "Governanca ativa: sem deploy automatico, sem publicacao automatica, "
    "sem API externa real, sem navegador automatico e sem mouse automatico."
)

packages = queue["packages"]

if not packages:
    st.warning("Nenhum pacote encontrado. Gere pacotes pelo Planning Approval Packager e atualize esta pagina.")
    st.stop()

labels = [
    f"{item['decision_status']} | {item['package_id']} | {item['title'][:80]}"
    for item in packages
]

selected_label = st.selectbox("Selecione um pacote", labels)
selected_index = labels.index(selected_label)
package = packages[selected_index]

with st.expander("Detalhes do pacote", expanded=True):
    st.write("Package ID:", package["package_id"])
    st.write("Status:", package["decision_status"])
    st.write("Risco:", package["risk_level"])
    st.write("Origem:", package["source_path"])
    st.write("Resumo:", package["summary"])

decision = st.radio(
    "Decisao humana",
    options=list(ALLOWED_DECISIONS.keys()),
    format_func=lambda key: ALLOWED_DECISIONS[key]["label_pt"],
    horizontal=True,
)

operator = st.text_input("Operador", value="human_operator")
reason = st.text_area("Justificativa obrigatoria", height=140)

if st.button("Registrar decisao", type="primary"):
    try:
        record = record_decision(
            package_id=package["package_id"],
            decision=decision,
            reason=reason,
            operator=operator,
            stage=int(stage),
        )
        st.success(f"Decisao registrada: {record['decision_id']} - {record['status']}")
        st.code(record["audit"]["decision_file"], language="text")
    except Exception as exc:
        st.error(str(exc))

st.divider()
st.caption(
    "Arquivos principais: live/human_decision_center/decision_queue.json | "
    "memory/human_decision_center/decisions.jsonl | reports/human_decision_center/"
)
