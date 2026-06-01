from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_rollback_sandbox_review_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "rollback_sandbox_review" / "latest_agent_rollback_sandbox_review_report.json"
REVIEW_PATH = PROJECT_ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_operator_review.json"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_executive_summary.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "rollback_sandbox_review" / "latest_rollback_sandbox_review_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "rollback_sandbox_review" / "k_os_agent_rollback_sandbox_review_policy.json"

st.set_page_config(page_title="K-OS Rollback Sandbox Review", layout="wide")

st.title("K-OS Agent Rollback Sandbox Report and Operator Review Core")
st.caption("Checkpoint 059 - relatório executivo da sandbox e revisão humana.")

st.warning("Este módulo não executa rollback real, não apaga dados, não altera arquivos e não executa shell.")


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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Revisão", "Resumo executivo", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Registrar revisão segura"):
            run([
                "--mode", "review",
                "--decision", "acknowledge_blocked",
                "--operator", "operator_k_os",
                "--notes", "operator acknowledges sandbox blockers and keeps rollback blocked"
            ])

    with c3:
        if st.button("Validar última"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Revisões", metrics.get("review_count", 0))

        with m2:
            st.metric("Registradas", metrics.get("review_recorded_count", 0))

        with m3:
            st.metric("Mudanças pedidas", metrics.get("changes_requested_count", 0))

        with m4:
            st.metric("Rollback real", metrics.get("rollback_execution_count", 0))

        st.subheader("Revisões recentes")
        st.dataframe(report.get("recent_reviews", []), use_container_width=True)

with tab2:
    decision = st.selectbox("Decision", ["acknowledge_blocked", "request_changes", "archive_review"])
    operator = st.text_input("Operator", value="operator_k_os")
    notes = st.text_input("Notes", value="operator acknowledges sandbox blockers and keeps rollback blocked")

    if st.button("Registrar revisão", type="primary"):
        run([
            "--mode", "review",
            "--decision", decision,
            "--operator", operator,
            "--notes", notes
        ])

    review = read_json(REVIEW_PATH)
    if review:
        st.subheader("Última revisão")
        st.json(review)

with tab3:
    summary = read_json(SUMMARY_PATH)
    if summary:
        st.json(summary)
    else:
        st.info("Nenhum resumo executivo registrado.")

with tab4:
    validation = read_json(VALIDATION_PATH)
    if validation:
        st.json(validation)
    else:
        st.info("Nenhuma validação registrada.")

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")