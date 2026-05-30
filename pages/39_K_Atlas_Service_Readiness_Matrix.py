from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.service_readiness_matrix.matrix import ServiceReadinessMatrix
from k_atlas.core.service_readiness_matrix.policy import validate_service_readiness_payload


REPORT = Path("reports/service_readiness_matrix/latest_service_readiness_matrix.json")

st.set_page_config(page_title="K-Atlas Service Readiness Matrix", layout="wide")

st.title("K-Atlas Service Readiness Matrix")
st.caption("Matriz central de prontidão operacional. Apenas leitura e consolidação.")

matrix = ServiceReadinessMatrix()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Serviços", summary.get("services_total", 0))

with col2:
    st.metric("Prontos", summary.get("services_ready", 0))

with col3:
    st.metric("Bloqueados", summary.get("services_blocked", 0))

with col4:
    st.metric("Score médio", summary.get("avg_score", 0))

st.divider()

tab_run, tab_layers, tab_services, tab_git, tab_report = st.tabs([
    "Atualizar",
    "Camadas",
    "Serviços",
    "Git",
    "Relatório",
])

with tab_run:
    scope = st.selectbox("Escopo", ["all", "core", "social", "saas", "external", "ops", "creative"])

    payload = {
        "scope": scope,
        "objective": "consolidar prontidao operacional",
        "live_call": False,
        "real_execute": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "mass_messaging": False,
        "browser_automation": False,
        "bypass_human_approval": False,
    }

    st.json(payload)

    if st.button("Atualizar matriz", type="primary"):
        validation = validate_service_readiness_payload(payload)
        if not validation["ok"]:
            st.error("Payload bloqueado pela política.")
            st.json(validation)
        else:
            result = matrix.generate(payload)
            st.success("Matriz atualizada.")
            st.json(result)

    if latest:
        st.subheader("Próxima ação")
        st.info(summary.get("next_action", "sem recomendação"))

with tab_layers:
    if not latest:
        st.info("Nenhuma matriz ainda.")
    else:
        for name, item in latest.get("layers", {}).items():
            with st.expander(f"{name} | score {item.get('avg_score')}"):
                st.json(item)

with tab_services:
    if not latest:
        st.info("Nenhum serviço ainda.")
    else:
        for item in latest.get("services", []):
            with st.expander(f"{item.get('service')} | {item.get('readiness')} | score {item.get('score')}"):
                st.json(item)

with tab_git:
    if not latest:
        st.info("Sem dados de Git.")
    else:
        st.subheader("Git status")
        st.code(latest.get("git", {}).get("status", {}).get("stdout", ""), language="text")

        st.subheader("Últimos commits")
        st.code(latest.get("git", {}).get("log", {}).get("stdout", ""), language="text")

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
