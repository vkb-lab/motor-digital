from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_dry_run_executor_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_executor_report.json"
RESULT_PATH = PROJECT_ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_result.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "dry_run_executor" / "latest_agent_dry_run_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "dry_run_executor" / "k_os_agent_dry_run_executor_policy.json"

st.set_page_config(page_title="K-OS Agent Dry Run Executor", layout="wide")

st.title("K-OS Agent Dry Run Executor Core")
st.caption("Checkpoint 046 - execução simulada, sem efeitos reais, com evidência auditável.")

st.warning(
    "Dry-run apenas. Nenhum efeito real, envio externo, publicação externa ou execução real sem approval."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Executar dry-run", "Resultado", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Auditar"):
            run(["--mode", "audit"])

    with c3:
        if st.button("Validar último"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Dry-runs", metrics.get("dry_run_count", 0))

        with m2:
            st.metric("Ready review", metrics.get("ready_for_review_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Execução real", metrics.get("real_execution_count", 0))

        st.subheader("Dry-runs recentes")
        st.dataframe(report.get("recent_dry_runs", []), use_container_width=True)

with tab2:
    reason = st.text_input("Reason", value="operator_dry_run_execution")

    if st.button("Executar dry-run", type="primary"):
        run(["--mode", "execute", "--reason", reason])

with tab3:
    result = read_json(RESULT_PATH)
    validation = read_json(VALIDATION_PATH)

    if result:
        st.subheader("Último resultado")
        st.json(result)

    if validation:
        st.subheader("Validação")
        st.json(validation)

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")