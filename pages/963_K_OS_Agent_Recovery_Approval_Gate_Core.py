from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_recovery_gate_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "recovery_gate" / "latest_agent_recovery_gate_report.json"
GATE_PATH = PROJECT_ROOT / "reports" / "recovery_gate" / "latest_recovery_gate_record.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "recovery_gate" / "latest_recovery_gate_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "recovery_gate" / "k_os_agent_recovery_gate_policy.json"

st.set_page_config(page_title="K-OS Recovery Gate", layout="wide")

st.title("K-OS Agent Recovery Approval Gate Core")
st.caption("Checkpoint 063 - gate governado para recovery futuro.")

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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Gate", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Bloquear recovery"):
            run([
                "--mode", "gate",
                "--gate-mode", "block_recovery",
                "--operator", "operator_k_os",
                "--confirmation", "block recovery execution",
                "--reason", "operator_safe_block"
            ])

    with c3:
        if st.button("Validar último"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Registros", metrics.get("gate_record_count", 0))

        with m2:
            st.metric("Aprovados", metrics.get("approved_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Recovery real", metrics.get("recovery_execution_count", 0))

        st.subheader("Registros recentes")
        st.dataframe(report.get("recent_gate_records", []), use_container_width=True)

with tab2:
    gate_mode = st.selectbox("Gate mode", ["block_recovery", "approve_future_recovery", "revoke_recovery"])
    operator = st.text_input("Operator", value="operator_k_os")
    confirmation = st.text_input("Confirmation", value="block recovery execution")
    reason = st.text_input("Reason", value="operator_recovery_gate")

    if st.button("Registrar gate", type="primary"):
        run([
            "--mode", "gate",
            "--gate-mode", gate_mode,
            "--operator", operator,
            "--confirmation", confirmation,
            "--reason", reason
        ])

    record = read_json(GATE_PATH)
    if record:
        st.subheader("Último gate")
        st.json(record)

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