from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_recovery_readiness_matrix_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "recovery_readiness_matrix" / "latest_agent_recovery_readiness_matrix_report.json"
MATRIX_PATH = PROJECT_ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "recovery_readiness_matrix" / "latest_recovery_readiness_matrix_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "recovery_readiness_matrix" / "k_os_agent_recovery_readiness_matrix_policy.json"

st.set_page_config(page_title="K-OS Recovery Readiness Matrix", layout="wide")

st.title("K-OS Agent Recovery Readiness Matrix Core")
st.caption("Checkpoint 061 - matriz de prontidão de recovery controlado.")

st.warning("Este módulo não executa recovery, rollback, git reset, force push ou shell.")


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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Matriz", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Gerar matriz"):
            run(["--mode", "build", "--operator", "operator_k_os", "--reason", "operator_recovery_readiness_matrix"])

    with c3:
        if st.button("Validar última"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Matrizes", metrics.get("matrix_count", 0))

        with m2:
            st.metric("Controlled ready", metrics.get("controlled_ready_count", 0))

        with m3:
            st.metric("Review required", metrics.get("review_required_count", 0))

        with m4:
            st.metric("Recovery real", metrics.get("recovery_execution_count", 0))

        st.subheader("Matrizes recentes")
        st.dataframe(report.get("recent_matrices", []), use_container_width=True)

with tab2:
    matrix = read_json(MATRIX_PATH)
    if matrix:
        st.subheader("Última matriz")
        st.metric("Readiness score", str(matrix.get("readiness_score")) + "/" + str(matrix.get("max_score")))
        st.metric("Readiness level", matrix.get("readiness_level"))
        st.metric("Risk level", matrix.get("risk_level"))
        st.json(matrix)
    else:
        st.info("Nenhuma matriz registrada.")

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