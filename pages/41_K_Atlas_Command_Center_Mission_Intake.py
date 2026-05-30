from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.command_center_mission_intake.intake import CommandCenterMissionIntake
from k_atlas.core.command_center_mission_intake.policy import validate_command_center_intake_payload


REPORT = Path("reports/command_center_mission_intake/latest_command_center_mission_intake.json")

st.set_page_config(page_title="K-Atlas Command Center Mission Intake", layout="wide")

st.title("K-Atlas Command Center Mission Intake")
st.caption("Importa missões aprovadas para fila do Command Center. Não executa tarefas.")

intake = CommandCenterMissionIntake()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else intake.save_report()
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Tasks no Command Center", summary.get("command_center_tasks_total", latest.get("tasks_imported", 0)))

with col2:
    st.metric("Intakes", summary.get("intakes_total", latest.get("exports_processed", 0)))

with col3:
    st.metric("Fila planning", summary.get("queued_for_planning", 0))

with col4:
    st.metric("Execução real", str(summary.get("real_execution_enabled", latest.get("real_execution_enabled", False))))

st.divider()

tab_process, tab_manual, tab_queue, tab_report = st.tabs(["Processar exports", "Intake manual", "Fila Command Center", "Relatório"])

with tab_process:
    st.warning("Processa exports da Operator Mission Queue. Não executa nenhuma tarefa.")

    limit = st.number_input("Limite de exports", min_value=1, max_value=100, value=25)

    if st.button("Processar exports aprovados", type="primary"):
        result = intake.process_exports(limit=int(limit))
        st.success("Exports processados sem execução real.")
        st.json(result)

with tab_manual:
    payload_text = st.text_area(
        "Payload manual",
        value=json.dumps(intake.default_payload(), ensure_ascii=False, indent=2),
        height=420,
    )

    if st.button("Importar payload manual"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_command_center_intake_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = intake.intake_payload(payload)
                st.success("Payload importado para fila do Command Center.")
                st.json(result)

with tab_queue:
    current = intake.summary()
    queue = current.get("queue", [])

    if not queue:
        st.info("Fila do Command Center vazia.")
    else:
        for item in queue:
            with st.expander(f"{item.get('status')} | {item.get('objective')}"):
                st.json(item)

with tab_report:
    st.json(intake.save_report())
