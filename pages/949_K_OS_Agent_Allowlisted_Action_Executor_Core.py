from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_allowlisted_action_executor_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "allowlisted_action_executor" / "latest_agent_allowlisted_action_executor_report.json"
EXECUTION_PATH = PROJECT_ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "allowlisted_action_executor" / "latest_allowlisted_action_execution_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "allowlisted_action_executor" / "k_os_agent_allowlisted_action_executor_policy.json"

st.set_page_config(page_title="K-OS Allowlisted Action Executor", layout="wide")

st.title("K-OS Agent Allowlisted Action Executor Core")
st.caption("Checkpoint 049 - executor interno com allowlist, rota segura e bloqueio de comando arbitrário.")

st.warning(
    "Executa somente ações internas permitidas. Sem shell arbitrário, sem envio externo e sem publicação externa."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Executar ação", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Auditar"):
            run(["--mode", "audit"])

    with c3:
        if st.button("Validar última"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Execuções", metrics.get("execution_count", 0))

        with m2:
            st.metric("Executadas", metrics.get("executed_count", 0))

        with m3:
            st.metric("Bloqueadas", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Shell", metrics.get("shell_command_count", 0))

        st.subheader("Execuções recentes")
        st.dataframe(report.get("recent_executions", []), use_container_width=True)

with tab2:
    action = st.selectbox(
        "Ação allowlisted",
        [
            "safe_internal_noop",
            "cockpit_audit",
            "analytics_audit",
            "security_scan_staged",
            "memory_bus_audit",
            "context_api_audit",
            "agent_runtime_audit",
            "agent_queue_audit"
        ]
    )
    operator = st.text_input("Operator", value="operator_k_os")
    reason = st.text_input("Reason", value="operator_allowlisted_action_execution")

    if st.button("Executar ação permitida", type="primary"):
        run(["--mode", "execute", "--action", action, "--operator", operator, "--reason", reason])

    execution = read_json(EXECUTION_PATH)
    if execution:
        st.subheader("Última execução")
        st.json(execution)

with tab3:
    validation = read_json(VALIDATION_PATH)
    if validation:
        st.json(validation)
    else:
        st.info("Nenhuma validação registrada.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")