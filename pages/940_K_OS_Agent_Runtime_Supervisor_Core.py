from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_runtime_supervisor_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_supervisor_report.json"
WATCHDOG_PATH = PROJECT_ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_watchdog_report.json"
HEARTBEAT_PATH = PROJECT_ROOT / "reports" / "agent_runtime" / "latest_agent_runtime_heartbeat_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "agent_runtime" / "k_os_agent_runtime_supervisor_policy.json"

st.set_page_config(page_title="K-OS Agent Runtime Supervisor", layout="wide")

st.title("K-OS Agent Runtime Supervisor")
st.caption("Checkpoint 040 - heartbeat, watchdog, runtime status e supervisão multiagente.")

st.warning(
    "Supervisor local. Não executa comando arbitrário. Não publica dados externos. Estado bruto fica fora do GitHub."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Heartbeat", "Watchdog", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar supervisor", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo runtime"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar supervisor"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})
        watchdog = report.get("watchdog", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Health", watchdog.get("health_level", "unknown"))

        with m2:
            st.metric("Agentes", metrics.get("agent_count", 0))

        with m3:
            st.metric("Saudáveis", metrics.get("healthy_agent_count", 0))

        with m4:
            st.metric("Stale", metrics.get("stale_agent_count", 0))

        with m5:
            st.metric("Queue tasks", metrics.get("queue_task_count", 0))

        st.subheader("Agentes")
        st.dataframe(report.get("agents", []), use_container_width=True)

        st.subheader("Eventos recentes")
        st.dataframe(report.get("recent_runtime_events", []), use_container_width=True)

with tab2:
    agent_id = st.selectbox(
        "Agent ID",
        [
            "k_atlas_engineer",
            "k_uni_cockpit",
            "k_os_git_bridge",
            "k_os_security_firewall",
            "k_os_schema_guard",
            "marketplace_ia_agent",
            "future_multimodal_connector"
        ]
    )

    task_id = st.text_input("Task ID", value="manual_runtime_task")
    action_id = st.text_input("Action ID", value="cockpit_audit")
    runtime_status = st.selectbox("Runtime status", ["idle", "active", "waiting_approval", "completed", "failed"])
    reason = st.text_input("Motivo", value="operator_heartbeat")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Registrar agente", type="primary"):
            run(["--mode", "register-agent", "--agent-id", agent_id, "--reason", reason])

    with c2:
        if st.button("Enviar heartbeat"):
            run([
                "--mode", "heartbeat",
                "--agent-id", agent_id,
                "--task-id", task_id,
                "--action-id", action_id,
                "--status", runtime_status,
                "--reason", reason
            ])

    heartbeat = read_json(HEARTBEAT_PATH)
    if heartbeat:
        st.subheader("Último heartbeat")
        st.json(heartbeat)

with tab3:
    if st.button("Rodar watchdog", type="primary"):
        run(["--mode", "watchdog"])

    watchdog = read_json(WATCHDOG_PATH)
    if watchdog:
        st.metric("Health", watchdog.get("health_level", "unknown"))
        st.json(watchdog)

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")