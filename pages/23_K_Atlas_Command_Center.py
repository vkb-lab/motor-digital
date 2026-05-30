from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.command_center.center import CommandCenter

QUEUE = Path("memory/command_center/command_queue.json")
REPORT = Path("reports/command_center/latest_command_center_run.json")

st.set_page_config(page_title="K-Atlas Command Center", layout="wide")

st.title("K-Atlas Command Center Autônomo")
st.caption("Ciclos supervisionados: saúde, Git, daemon, relatórios, sandbox criativo e deploy assistido.")

center = CommandCenter()
queue = center.load_queue()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}

pending = [x for x in queue if x.get("status") == "pending"]
finished = [x for x in queue if x.get("status") == "finished"]
blocked = [x for x in queue if x.get("status") == "blocked"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Fila total", len(queue))
with col2:
    st.metric("Pendentes", len(pending))
with col3:
    st.metric("Finalizadas", len(finished))
with col4:
    st.metric("Bloqueadas", len(blocked))

st.divider()

tab_run, tab_queue, tab_report = st.tabs(["Rodar ciclo", "Fila", "Último relatório"])

with tab_run:
    objective = st.text_area("Objetivo do ciclo", value="manter K-Atlas operacional e gerar relatório de progresso", height=120)

    if st.button("Criar ciclo", type="primary"):
        result = center.create_cycle(objective)
        st.success("Ciclo criado.")
        st.json(result)

    if st.button("Executar pendentes agora"):
        result = center.run_pending_once(limit=10)
        st.success("Execução concluída.")
        st.json(result)

with tab_queue:
    if not queue:
        st.info("Fila vazia.")
    else:
        for task in reversed(queue[-80:]):
            with st.expander(f"{task.get('status')} | {task.get('action')} | {task.get('task_id')}"):
                st.json(task)

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório do Command Center ainda.")
