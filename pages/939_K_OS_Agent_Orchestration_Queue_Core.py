from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_orchestration_queue_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "agent_queue" / "latest_agent_orchestration_queue_report.json"
SNAPSHOT_PATH = PROJECT_ROOT / "reports" / "agent_queue" / "latest_agent_queue_snapshot.json"
DISPATCH_PATH = PROJECT_ROOT / "reports" / "agent_queue" / "latest_agent_dispatch_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "agent_queue" / "k_os_agent_orchestration_queue_policy.json"
COMMAND_CATALOG_PATH = PROJECT_ROOT / "reports" / "command_center" / "latest_action_catalog.json"

st.set_page_config(page_title="K-OS Agent Queue", layout="wide")

st.title("K-OS Agent Orchestration Queue")
st.caption("Checkpoint 039 - fila governada de agentes, dispatch via Command Center e dry-run por padrão.")

st.warning(
    "Fila local. Nenhum agente executa comando arbitrário. Dispatch acontece via Command Center e exige gates."
)


def python_exe() -> str:
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
    ]
    for item in candidates:
        if item.exists():
            return str(item)
    return "python"


def run(args: list[str]) -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    st.code(" ".join(completed.args), language="powershell")

    if completed.stdout:
        st.code(completed.stdout, language="json")

    if completed.stderr:
        st.code(completed.stderr, language="text")

    if completed.returncode == 0:
        st.success("OK")
    else:
        st.error(f"Falhou: {completed.returncode}")


def read_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {}


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Criar tarefa", "Aprovar/Dispatch", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar fila", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar fila"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Tarefas", metrics.get("task_count", 0))

        with m2:
            st.metric("Dispatches", metrics.get("dispatch_count", 0))

        with m3:
            st.metric("Bloqueadas", metrics.get("blocked_task_count", 0))

        with m4:
            st.metric("Aprovadas", metrics.get("approved_task_count", 0))

        st.subheader("Tarefas")
        st.dataframe(report.get("tasks", []), use_container_width=True)

        st.subheader("Dispatches recentes")
        st.dataframe(report.get("recent_dispatches", []), use_container_width=True)

    snapshot = read_json(SNAPSHOT_PATH)
    if snapshot:
        st.subheader("Snapshot da fila")
        st.json(snapshot)

with tab2:
    catalog = read_json(COMMAND_CATALOG_PATH)
    actions = catalog.get("actions", [])

    action_ids = [item.get("action_id") for item in actions] or ["cockpit_audit"]

    agent_id = st.selectbox(
        "Agent ID",
        [
            "k_atlas_engineer",
            "k_uni_cockpit",
            "k_os_security_firewall",
            "k_os_schema_guard",
            "marketplace_ia_agent",
            "future_multimodal_connector"
        ]
    )
    action_id = st.selectbox("Action ID do Command Center", action_ids)
    title = st.text_input("Título", value="Tarefa controlada via fila de agentes")
    priority = st.selectbox("Prioridade", ["low", "medium", "high", "critical"], index=1)
    reason = st.text_input("Motivo", value="operator_queue_request")

    if st.button("Criar tarefa", type="primary"):
        run([
            "--mode", "create-task",
            "--agent-id", agent_id,
            "--action-id", action_id,
            "--title", title,
            "--priority", priority,
            "--reason", reason
        ])

with tab3:
    task_id = st.text_input("Task ID")
    approval_reason = st.text_input("Motivo/aprovação", value="operator_approval")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Aprovar tarefa", type="primary"):
            run(["--mode", "approve-task", "--task-id", task_id, "--reason", approval_reason])

    with c2:
        execute = st.checkbox("Executar de verdade, não apenas dry-run")
        approved = st.checkbox("Enviar approval ao Command Center")

        args = ["--mode", "dispatch-task", "--task-id", task_id, "--reason", approval_reason]

        if execute:
            args.append("--execute")

        if approved:
            args.append("--approved")

        if st.button("Dispatch controlado"):
            run(args)

    dispatch = read_json(DISPATCH_PATH)
    if dispatch:
        st.subheader("Último dispatch")
        st.json(dispatch)

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")