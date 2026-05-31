from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_prompt_assembly_execution_plan_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_assembly_report.json"
PROMPT_PATH = PROJECT_ROOT / "reports" / "prompt_assembly" / "latest_agent_prompt_package.json"
PLAN_PATH = PROJECT_ROOT / "reports" / "prompt_assembly" / "latest_agent_execution_plan.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "prompt_assembly" / "latest_prompt_assembly_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "prompt_assembly" / "k_os_agent_prompt_assembly_policy.json"

st.set_page_config(page_title="K-OS Prompt Assembly", layout="wide")

st.title("K-OS Agent Prompt Assembly and Execution Plan")
st.caption("Checkpoint 045 - prompt operacional sanitizado e plano de execução governado.")

st.warning(
    "Camada local. Sem payload bruto, sem secrets, sem envio externo e sem execução real sem approval."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Montar prompt", "Plano/Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Prompt packages", metrics.get("prompt_package_count", 0))

        with m2:
            st.metric("Validados", metrics.get("validated_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Secrets", metrics.get("secret_package_count", 0))

        st.subheader("Prompt packages recentes")
        st.dataframe(report.get("recent_prompt_packages", []), use_container_width=True)

with tab2:
    agent_id = st.text_input("Agent ID", value="k_atlas_engineer")
    task_id = st.text_input("Task ID", value="manual_prompt_task")
    action_id = st.text_input("Action ID", value="cockpit_audit")
    query = st.text_input("Query", value="agent")
    reason = st.text_input("Reason", value="operator_prompt_assembly")

    if st.button("Montar prompt operacional", type="primary"):
        run([
            "--mode", "assemble",
            "--agent-id", agent_id,
            "--task-id", task_id,
            "--action-id", action_id,
            "--query", query,
            "--reason", reason
        ])

    prompt = read_json(PROMPT_PATH)
    if prompt:
        st.subheader("Último prompt package")
        st.json(prompt)

with tab3:
    if st.button("Validar último prompt", type="primary"):
        run(["--mode", "validate-latest"])

    validation = read_json(VALIDATION_PATH)
    if validation:
        st.subheader("Validação")
        st.json(validation)

    plan = read_json(PLAN_PATH)
    if plan:
        st.subheader("Plano de execução")
        st.json(plan)

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")