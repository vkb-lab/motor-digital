from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.mission_executor_bridge.bridge import MissionExecutorBridge
from k_atlas.core.mission_executor_bridge.policy import validate_execution_payload


MISSION_PLAN = Path("reports/mission_planner/latest_mission_plan.json")
REPORT = Path("reports/mission_executor_bridge/latest_mission_executor_bridge.json")

st.set_page_config(page_title="K-Atlas Mission Executor Bridge", layout="wide")

st.title("K-Atlas Mission Executor Bridge")
st.caption("Executa missões planejadas com rastreio, dry run e governança humana.")

latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
plan = json.loads(MISSION_PLAN.read_text(encoding="utf-8")) if MISSION_PLAN.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Mission ID", latest.get("mission_id", "none"))

with col3:
    st.metric("Tasks executadas", len(latest.get("executed", [])) if latest else 0)

with col4:
    st.metric("Dry run", str(latest.get("dry_run", "none")))

st.divider()

tab_run, tab_plan, tab_report = st.tabs(["Executar ponte", "Plano atual", "Relatório"])

with tab_run:
    payload_text = st.text_area(
        "Payload de execução",
        value=json.dumps({
            "dry_run": True,
            "max_tasks": 10,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False
        }, ensure_ascii=False, indent=2),
        height=260,
    )

    if st.button("Executar missão planejada", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_execution_payload(payload)
            if not validation["ok"]:
                st.error("Execução bloqueada pela política.")
                st.json(validation)
            else:
                result = MissionExecutorBridge().execute_plan(payload=payload)
                if result["ok"]:
                    st.success("Mission Executor Bridge concluído.")
                else:
                    st.warning("Execução precisa de revisão.")
                st.json(result)

with tab_plan:
    if plan:
        st.json(plan)
    else:
        st.warning("Nenhum plano encontrado. Rode o Mission Planner primeiro.")

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório do Executor Bridge ainda.")
