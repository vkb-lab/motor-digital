# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.decision_flow_router import route_latest_decisions


st.set_page_config(
    page_title="K-Atlas Decision Flow Router",
    layout="wide",
)

st.title("K-Atlas Decision Flow Router")
st.caption("Roteamento local de decisoes humanas para continuidade supervisionada, bloqueio ou ajustes.")

stage = st.number_input("Etapa operacional", min_value=1, value=64, step=1)

if st.button("Atualizar rotas", type="primary"):
    st.session_state["route_result"] = route_latest_decisions(stage=int(stage))

if "route_result" not in st.session_state:
    st.session_state["route_result"] = route_latest_decisions(stage=int(stage))

result = st.session_state["route_result"]
summary = result["summary"]

col_total, col_approved, col_denied, col_adjustments = st.columns(4)

col_total.metric("Rotas", summary["routes_total"])
col_approved.metric("Aprovadas", summary["approved_routes"])
col_denied.metric("Bloqueadas", summary["denied_routes"])
col_adjustments.metric("Ajustes", summary["adjustment_routes"])

st.info(
    "Governanca ativa: sem deploy automatico, sem publicacao automatica, "
    "sem API externa real, sem navegador automatico e sem mouse automatico."
)

routes = result["routes"]

if not routes:
    st.warning("Nenhuma decisao humana roteavel encontrada.")
    st.stop()

for route in routes:
    with st.expander(f"{route['route_type']} | {route['package_id']}", expanded=False):
        st.write("Route ID:", route["route_id"])
        st.write("Decisao humana:", route["human_decision"])
        st.write("Status humano:", route["human_status"])
        st.write("Proxima acao:", route["next_action"])
        st.write("Operador:", route["operator"])
        st.write("Justificativa:", route["human_reason"])
        st.write("Artefato:", route.get("route_artifact_path", "nao gerado"))

st.divider()
st.caption(
    "Arquivos principais: live/decision_flow_router/routed_decisions.json | "
    "live/supervised_continuation_queue/stage_064_supervised_continuation_queue.json | "
    "memory/decision_flow_router/routes.jsonl"
)
