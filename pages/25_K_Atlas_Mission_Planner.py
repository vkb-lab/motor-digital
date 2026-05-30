from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.mission_planner.planner import MissionPlanner
from k_atlas.core.mission_planner.policy import validate_mission_payload


REPORT = Path("reports/mission_planner/latest_mission_plan.json")
REQUEST = Path("reports/mission_planner/latest_mission_execution_request.json")

st.set_page_config(page_title="K-Atlas Mission Planner", layout="wide")

st.title("K-Atlas Autonomy Mission Planner")
st.caption("Transforma missão em tarefas seguras para o Command Center.")

planner = MissionPlanner()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
request = json.loads(REQUEST.read_text(encoding="utf-8")) if REQUEST.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Última missão", latest.get("status", "none"))

with col2:
    st.metric("Tasks", len(latest.get("tasks", [])) if latest else 0)

with col3:
    st.metric("Checkpoint", latest.get("checkpoint", "none") if latest else "none")

with col4:
    st.metric("Fila", request.get("enqueue", {}).get("tasks_enqueued", 0) if request else 0)

st.divider()

tab_create, tab_latest, tab_request = st.tabs(["Criar missão", "Último plano", "Último enqueue"])

with tab_create:
    payload_text = st.text_area(
        "Payload da missão",
        value=json.dumps(planner.default_payload(), ensure_ascii=False, indent=2),
        height=360,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Gerar plano", type="primary"):
            try:
                payload = json.loads(payload_text)
            except json.JSONDecodeError as exc:
                st.error(f"JSON inválido: {exc}")
            else:
                validation = validate_mission_payload(payload)
                if not validation["ok"]:
                    st.error("Missão bloqueada pela política.")
                    st.json(validation)
                else:
                    result = planner.build_plan(payload)
                    st.success("Plano gerado.")
                    st.json(result)

    with col_b:
        if st.button("Gerar plano e enviar ao Command Center"):
            try:
                payload = json.loads(payload_text)
            except json.JSONDecodeError as exc:
                st.error(f"JSON inválido: {exc}")
            else:
                result = planner.plan_and_enqueue(payload)
                if result["ok"]:
                    st.success("Missão enviada para o Command Center.")
                else:
                    st.error("Missão bloqueada.")
                st.json(result)

with tab_latest:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum plano ainda.")

with tab_request:
    if request:
        st.json(request)
    else:
        st.info("Nenhum envio ao Command Center ainda.")
