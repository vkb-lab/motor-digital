from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_resilience_drill_operator_review_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "resilience_drill_operator_review" / "latest_agent_resilience_drill_operator_review_report.json"
REVIEW_PATH = PROJECT_ROOT / "reports" / "resilience_drill_operator_review" / "latest_resilience_drill_operator_review.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "resilience_drill_operator_review" / "latest_resilience_drill_operator_review_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "resilience_drill_operator_review" / "k_os_agent_resilience_drill_operator_review_policy.json"

st.set_page_config(page_title="K-OS Resilience Drill Operator Review", layout="wide")

st.title("K-OS Agent Resilience Drill Operator Review Core")
st.caption("Checkpoint 075 - revisao humana dos dry runs de resiliencia.")

st.warning("Este modulo registra revisao humana, mas nao executa drill, recovery, rollback, git reset, force push ou shell.")


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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Review", "Validacao", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Registrar revisao"):
            run([
                "--mode", "review",
                "--operator", "operator_k_os",
                "--decision", "reviewed_with_followup",
                "--notes", "operator_review_recorded_in_cockpit",
                "--reason", "operator_resilience_drill_review"
            ])

    with c3:
        if st.button("Validar ultima"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Reviews", metrics.get("review_count", 0))

        with m2:
            st.metric("Recorded", metrics.get("operator_review_recorded_count", 0))

        with m3:
            st.metric("Followup", metrics.get("operator_review_requires_followup_count", 0))

        with m4:
            st.metric("Drill real", metrics.get("drill_execution_count", 0))

        st.subheader("Reviews recentes")
        st.dataframe(report.get("recent_reviews", []), use_container_width=True)

with tab2:
    review = read_json(REVIEW_PATH)
    if review:
        st.json(review)
    else:
        st.info("Nenhuma revisao registrada.")

with tab3:
    validation = read_json(VALIDATION_PATH)
    if validation:
        st.json(validation)
    else:
        st.info("Nenhuma validacao registrada.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda nao encontrada.")