from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.command_center.scheduler import CommandCenterScheduler


STATE = Path("memory/command_center_scheduler/scheduler_state.json")
EVENTS = Path("memory/command_center_scheduler/events.jsonl")
PIDS = Path("memory/command_center_scheduler/pids.json")

st.set_page_config(page_title="K-Atlas Command Scheduler", layout="wide")

st.title("K-Atlas Command Center Scheduler 24/7")
st.caption("Executa ciclos supervisionados do Command Center em intervalo automático.")

state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
pids = json.loads(PIDS.read_text(encoding="utf-8")) if PIDS.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", state.get("status", "offline"))

with col2:
    st.metric("Checkpoint", state.get("checkpoint", "none"))

with col3:
    st.metric("Última execução", state.get("timestamp", "none"))

with col4:
    st.metric("PID", pids.get("scheduler_pid", "none"))

st.divider()

tab_run, tab_state, tab_events, tab_commands = st.tabs(["Rodar agora", "Estado", "Eventos", "Comandos"])

with tab_run:
    objective = st.text_area(
        "Objetivo do ciclo",
        value="manter K-Atlas operacional, auditado e reportado",
        height=120,
    )

    if st.button("Rodar ciclo agora", type="primary"):
        result = CommandCenterScheduler().run_once(objective=objective, execute_tasks=True)
        st.success("Ciclo do scheduler executado.")
        st.json(result)

with tab_state:
    if state:
        st.json(state)
    else:
        st.warning("Nenhum estado encontrado. Inicie o scheduler.")

with tab_events:
    if not EVENTS.exists():
        st.info("Nenhum evento ainda.")
    else:
        rows = []
        for line in EVENTS.read_text(encoding="utf-8").splitlines()[-80:]:
            if line.strip():
                rows.append(json.loads(line))

        for row in reversed(rows):
            with st.expander(f"{row.get('timestamp')} | {row.get('event_type')}"):
                st.json(row)

with tab_commands:
    st.code(
        'powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\start_command_center_scheduler_window.ps1"',
        language="powershell",
    )
    st.code(
        'powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\stop_command_center_scheduler.ps1"',
        language="powershell",
    )
    st.code(
        'powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\install_command_center_scheduler_startup.ps1"',
        language="powershell",
    )
