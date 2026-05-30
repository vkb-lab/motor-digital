from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.daily_operator.cockpit import DailyOperatorCockpit


REPORT = Path("reports/daily_operator/latest_daily_operator_cockpit.json")

st.set_page_config(page_title="K-Atlas Daily Operator Cockpit", layout="wide")

st.title("K-Atlas Daily Operator Cockpit")
st.caption("Painel diário do operador: estado do sistema, módulos, Git, Render e próxima ação.")

if st.button("Atualizar cockpit", type="primary"):
    result = DailyOperatorCockpit().collect()
    st.success("Cockpit atualizado.")
    st.json(result)

latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}

summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Módulos OK", f"{summary.get('healthy_modules', 0)}/{summary.get('total_modules', 0)}")

with col2:
    st.metric("Streamlit", summary.get("streamlit", "unknown"))

with col3:
    st.metric("Render", summary.get("render", "unknown"))

with col4:
    st.metric("Git sujo", str(summary.get("git_dirty", "unknown")))

st.divider()

tab_overview, tab_modules, tab_git, tab_report = st.tabs(["Visão diária", "Módulos", "Git", "Relatório completo"])

with tab_overview:
    if not latest:
        st.warning("Nenhum relatório ainda. Clique em Atualizar cockpit.")
    else:
        st.subheader("Próxima ação recomendada")
        st.info(summary.get("next_action", "sem recomendação"))

        st.subheader("Guardrails")
        for item in latest.get("guardrails", []):
            st.write(f"- {item}")

with tab_modules:
    if not latest:
        st.info("Sem dados.")
    else:
        for name, item in latest.get("modules", {}).items():
            with st.expander(f"{name} | {item.get('status')}"):
                st.json(item)

with tab_git:
    if not latest:
        st.info("Sem dados.")
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
