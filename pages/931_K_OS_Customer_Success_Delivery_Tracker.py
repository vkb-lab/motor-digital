from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_customer_success_delivery_tracker.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "customer_success" / "latest_customer_success_delivery_report.json"
HEALTH_PATH = PROJECT_ROOT / "reports" / "customer_success" / "latest_customer_success_health_snapshot.json"
POLICY_PATH = PROJECT_ROOT / "config" / "customer_success" / "k_os_customer_success_delivery_policy.json"

st.set_page_config(page_title="K-OS Customer Success", layout="wide")

st.title("K-OS Customer Success and Delivery Tracker")
st.caption("Checkpoint 031 - entregas, tarefas, saúde do cliente, riscos e próximas ações.")

st.warning(
    "Customer Success local. Nenhuma mensagem externa é enviada. Dados brutos ficam fora do GitHub."
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Conta", "Tarefa", "Health", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Customer Success", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo local"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar CS"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Contas", metrics.get("account_count", 0))

        with m2:
            st.metric("Entregas", metrics.get("delivery_count", 0))

        with m3:
            st.metric("Tarefas abertas", metrics.get("open_task_count", 0))

        with m4:
            st.metric("Alto risco", metrics.get("high_risk_count", 0))

        with m5:
            st.metric("Health red", metrics.get("red_health_count", 0))

        st.subheader("Contas")
        st.dataframe(report.get("accounts", []), use_container_width=True)

        st.subheader("Entregas")
        st.dataframe(report.get("deliveries", []), use_container_width=True)

        st.subheader("Tarefas")
        st.dataframe(report.get("tasks", []), use_container_width=True)

with tab2:
    customer_alias = st.text_input("Customer alias", value="demo_customer")
    owner = st.text_input("Success owner", value="k_os_operator")

    if st.button("Criar conta CS", type="primary"):
        run(["--mode", "create-account", "--customer-alias", customer_alias, "--owner", owner])

with tab3:
    account_id = st.text_input("Success account ID")
    task_title = st.text_input("Título da tarefa", value="Revisar primeira entrega")
    priority = st.selectbox("Prioridade", ["low", "medium", "high", "critical"])
    due_date = st.text_input("Due date", value="")
    task_owner = st.text_input("Owner", value="k_os_operator")

    if st.button("Adicionar tarefa", type="primary"):
        run([
            "--mode", "add-task",
            "--account-id", account_id,
            "--title", task_title,
            "--priority", priority,
            "--owner", task_owner,
            "--due-date", due_date
        ])

    st.divider()

    task_id = st.text_input("Task ID")
    task_status = st.selectbox("Status da tarefa", ["todo", "doing", "blocked", "waiting_customer", "review", "done", "cancelled"])
    reason = st.text_input("Motivo", value="manual_update")

    if st.button("Atualizar tarefa"):
        run([
            "--mode", "set-task-status",
            "--task-id", task_id,
            "--status", task_status,
            "--reason", reason
        ])

with tab4:
    health_account_id = st.text_input("Account ID para health")
    health = st.selectbox("Health", ["green", "yellow", "red", "unknown"])
    risk = st.selectbox("Risk", ["low", "medium", "high", "critical"])
    next_action = st.text_input("Próxima ação", value="revisar plano de sucesso")

    if st.button("Atualizar health", type="primary"):
        run([
            "--mode", "set-health",
            "--account-id", health_account_id,
            "--health", health,
            "--risk-level", risk,
            "--next-action", next_action
        ])

    if HEALTH_PATH.exists():
        st.subheader("Health snapshot")
        st.json(json.loads(HEALTH_PATH.read_text(encoding="utf-8-sig")))

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")