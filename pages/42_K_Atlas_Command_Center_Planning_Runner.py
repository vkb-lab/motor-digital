from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.command_center_planning_runner.policy import validate_command_center_planning_payload
from k_atlas.core.command_center_planning_runner.runner import CommandCenterPlanningRunner


REPORT = Path("reports/command_center_planning_runner/latest_command_center_planning_runner.json")

st.set_page_config(page_title="K-Atlas Command Center Planning Runner", layout="wide")

st.title("K-Atlas Command Center Planning Runner")
st.caption("Transforma tarefas importadas em planos supervisionados. Nao executa comandos.")

runner = CommandCenterPlanningRunner()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else runner.save_report()
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Intake tasks", summary.get("intake_tasks_total", 0))

with col2:
    st.metric("Planning queue", summary.get("planning_queue_total", 0))

with col3:
    st.metric("Planos criados", summary.get("plans_created", 0))

with col4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()

tab_run, tab_plans, tab_queue, tab_report = st.tabs(["Rodar planning", "Planos", "Fila", "Relatorio"])

with tab_run:
    scope = st.selectbox("Escopo", ["all", "core", "social", "saas", "external", "ops", "creative", "growth"])
    limit = st.number_input("Limite", min_value=1, max_value=100, value=25)

    payload = {
        "scope": scope,
        "limit": int(limit),
        "objective": "planejar tarefas importadas no Command Center",
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

    if st.button("Gerar planos supervisionados", type="primary"):
        validation = validate_command_center_planning_payload(payload)
        if not validation["ok"]:
            st.error("Payload bloqueado pela politica.")
            st.json(validation)
        else:
            result = runner.run(payload)
            st.success("Planning concluido sem execucao real.")
            st.json(result)

with tab_plans:
    current = runner.summary()
    plans = current.get("planning_queue", [])

    if not plans:
        st.info("Nenhum plano ainda.")
    else:
        for item in plans:
            with st.expander(f"{item.get('status')} | {item.get('objective')}"):
                st.json(item)

with tab_queue:
    current = runner.summary()
    st.json({
        "summary": current.get("summary", {}),
        "runs": current.get("runs", []),
    })

with tab_report:
    st.json(runner.save_report())
