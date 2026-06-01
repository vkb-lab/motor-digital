from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_recovery_governance_summary_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "recovery_governance_summary" / "latest_agent_recovery_governance_summary_report.json"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "recovery_governance_summary" / "latest_recovery_governance_summary.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "recovery_governance_summary" / "latest_recovery_governance_summary_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "recovery_governance_summary" / "k_os_agent_recovery_governance_summary_policy.json"

st.set_page_config(page_title="K-OS Recovery Governance Summary", layout="wide")

st.title("K-OS Agent Recovery Governance Summary Core")
st.caption("Checkpoint 069 - resumo governado da camada 061-068.")

st.warning("Este módulo consolida evidências, mas não executa recovery, rollback, git reset, force push ou shell.")


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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Resumo", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Gerar resumo"):
            run([
                "--mode", "summarize",
                "--operator", "operator_k_os",
                "--reason", "operator_recovery_governance_summary_061_068"
            ])

    with c3:
        if st.button("Validar último"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Resumos", metrics.get("summary_count", 0))

        with m2:
            st.metric("Safe", metrics.get("closed_safe_count", 0))

        with m3:
            st.metric("Review", metrics.get("closed_with_review_required_count", 0))

        with m4:
            st.metric("Recovery real", metrics.get("recovery_execution_count", 0))

        st.subheader("Resumos recentes")
        st.dataframe(report.get("recent_summaries", []), use_container_width=True)

with tab2:
    summary = read_json(SUMMARY_PATH)
    if summary:
        st.subheader("Último resumo")
        st.json(summary)
    else:
        st.info("Nenhum resumo registrado.")

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