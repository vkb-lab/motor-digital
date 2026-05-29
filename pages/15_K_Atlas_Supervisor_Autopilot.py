from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue
from k_atlas.core.supervisor_autopilot.autopilot import SupervisorAutopilot
from k_atlas.core.supervisor_autopilot.policy import AutopilotPolicy


SUPERVISOR_QUEUE_PATH = Path("memory/control_plane/supervisor_queue.json")
RUNS_PATH = Path("memory/supervisor_autopilot/autopilot_runs.json")


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    return data if isinstance(data, list) else []


st.set_page_config(page_title="K-Atlas Supervisor Autopilot", layout="wide")

st.title("K-Atlas Supervisor Autopilot")
st.caption("Aprovação assistida para tarefas de baixo risco. Não executa, não publica, não usa API externa.")

queue = SupervisorQueue(SUPERVISOR_QUEUE_PATH)
policy = AutopilotPolicy()
autopilot = SupervisorAutopilot(
    supervisor_queue=queue,
    policy=policy,
    run_log_path=RUNS_PATH,
)

approvals = queue.load() if SUPERVISOR_QUEUE_PATH.exists() else []
pending = [item for item in approvals if item.get("status") == "pending_approval"]
runs = load_json_list(RUNS_PATH)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Pendentes", len(pending))

with col2:
    st.metric("Runs autopilot", len(runs))

with col3:
    st.metric("Modo", "baixo risco")

st.divider()

tab_run, tab_pending, tab_runs = st.tabs(["Rodar Autopilot", "Pendentes", "Histórico"])

with tab_run:
    st.subheader("Executar aprovação assistida")

    st.warning("O Autopilot apenas aprova tarefas seguras. Ele não executa e não publica.")

    if st.button("Rodar Supervisor Autopilot", type="primary"):
        result = autopilot.run_once(reviewer="streamlit_supervisor_autopilot")
        st.success("Autopilot executado.")
        st.json(result)

with tab_pending:
    st.subheader("Tarefas pendentes e decisão prevista")

    if not pending:
        st.info("Nenhuma tarefa pendente.")
    else:
        for item in reversed(pending[-50:]):
            decision = policy.evaluate(item)
            task = item.get("task", {})
            with st.expander(f"{task.get('agent_name')} | {task.get('action')} | {decision.status}"):
                st.json({
                    "approval": item,
                    "autopilot_decision": decision.to_dict(),
                })

with tab_runs:
    st.subheader("Histórico do Autopilot")

    runs = load_json_list(RUNS_PATH)

    if not runs:
        st.info("Nenhum run registrado.")
    else:
        for run in reversed(runs[-50:]):
            with st.expander(f"{run.get('created_at')} | approved={run.get('approved_count')} | blocked={run.get('blocked_count')}"):
                st.json(run)
