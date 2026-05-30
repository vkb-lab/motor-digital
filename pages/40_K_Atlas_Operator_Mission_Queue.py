from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.operator_mission_queue.policy import validate_operator_mission_payload
from k_atlas.core.operator_mission_queue.queue import OperatorMissionQueue


REPORT = Path("reports/operator_mission_queue/latest_operator_mission_queue.json")

st.set_page_config(page_title="K-Atlas Operator Mission Queue", layout="wide")

st.title("K-Atlas Operator Mission Queue")
st.caption("Fila de missões supervisionadas. Não executa ações externas.")

queue = OperatorMissionQueue()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else queue.save_report()
summary = latest.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total", summary.get("total", 0))

with col2:
    st.metric("Na fila", summary.get("queued", 0))

with col3:
    st.metric("Aprovadas", summary.get("approved_for_planning", 0))

with col4:
    st.metric("Exportadas", summary.get("exported_to_command_center_payload", 0))

st.divider()

tab_create, tab_queue, tab_approved, tab_report = st.tabs(["Criar missão", "Fila", "Aprovadas", "Relatório"])

with tab_create:
    payload_text = st.text_area(
        "Payload da missão",
        value=json.dumps(queue.default_payload(), ensure_ascii=False, indent=2),
        height=480,
    )

    if st.button("Adicionar missão à fila", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_operator_mission_payload(payload)
            if not validation["ok"]:
                st.error("Missão bloqueada pela política.")
                st.json(validation)
            else:
                result = queue.enqueue(payload)
                st.success("Missão adicionada à fila.")
                st.json(result)

with tab_queue:
    rows = queue.list_by_status("queued")
    if not rows:
        st.info("Nenhuma missão pendente.")
    else:
        for item in rows:
            payload = item.get("payload", {})
            with st.expander(f"{payload.get('title')} | {item.get('mission_id')}"):
                st.json(item)

                if st.button(f"Aprovar planejamento {item.get('mission_id')}", key=f"approve_{item.get('mission_id')}"):
                    result = queue.approve(
                        item.get("mission_id"),
                        reviewer="streamlit_operator",
                        notes="Aprovado no cockpit. Sem execução real.",
                    )
                    st.success("Missão aprovada para planejamento.")
                    st.json(result)

with tab_approved:
    rows = queue.list_by_status("approved_for_planning")
    if not rows:
        st.info("Nenhuma missão aprovada aguardando exportação.")
    else:
        for item in rows:
            payload = item.get("payload", {})
            with st.expander(f"{payload.get('title')} | {item.get('mission_id')}"):
                st.json(item)

                if st.button(f"Exportar para Command Center {item.get('mission_id')}", key=f"export_{item.get('mission_id')}"):
                    result = queue.export_command_center_tasks(item.get("mission_id"))
                    st.success("Payload exportado. Nenhuma execução real realizada.")
                    st.json(result)

with tab_report:
    st.json(queue.save_report())
