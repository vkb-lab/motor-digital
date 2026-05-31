from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_real_execution_approval_gate_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "real_execution_gate" / "latest_agent_real_execution_approval_gate_report.json"
DECISION_PATH = PROJECT_ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_decision.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "real_execution_gate" / "latest_real_execution_approval_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "real_execution_gate" / "k_os_agent_real_execution_approval_gate_policy.json"

st.set_page_config(page_title="K-OS Real Execution Approval Gate", layout="wide")

st.title("K-OS Agent Real Execution Approval Gate Core")
st.caption("Checkpoint 047 - aprovação humana auditável antes de qualquer execução real.")

st.warning(
    "Este gate não executa ação real. Ele apenas aprova, bloqueia ou revoga com registro auditável."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Decisão", "Validação", "Policy"])

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
            st.metric("Decisões", metrics.get("decision_count", 0))

        with m2:
            st.metric("Aprovadas", metrics.get("approved_count", 0))

        with m3:
            st.metric("Bloqueadas", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Execução real", metrics.get("real_execution_performed_count", 0))

        st.subheader("Decisões recentes")
        st.dataframe(report.get("recent_decisions", []), use_container_width=True)

with tab2:
    operator = st.text_input("Operator", value="operator_k_os")
    reason = st.text_input("Reason", value="operator_approval_after_validated_dry_run")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Aprovar", type="primary"):
            run(["--mode", "approve", "--operator", operator, "--reason", reason])

    with c2:
        if st.button("Bloquear"):
            run(["--mode", "block", "--operator", operator, "--reason", reason])

    with c3:
        if st.button("Revogar"):
            run(["--mode", "revoke", "--operator", operator, "--reason", reason])

    decision = read_json(DECISION_PATH)
    if decision:
        st.subheader("Última decisão sanitizada")
        st.json(decision)

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