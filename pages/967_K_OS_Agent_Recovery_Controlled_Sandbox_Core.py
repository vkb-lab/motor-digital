from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_recovery_controlled_sandbox_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "recovery_controlled_sandbox" / "latest_agent_recovery_controlled_sandbox_report.json"
SANDBOX_PATH = PROJECT_ROOT / "reports" / "recovery_controlled_sandbox" / "latest_recovery_controlled_sandbox_record.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "recovery_controlled_sandbox" / "latest_recovery_controlled_sandbox_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "recovery_controlled_sandbox" / "k_os_agent_recovery_controlled_sandbox_policy.json"

st.set_page_config(page_title="K-OS Recovery Controlled Sandbox", layout="wide")

st.title("K-OS Agent Recovery Controlled Execution Sandbox Core")
st.caption("Checkpoint 067 - sandbox controlada/local para recovery sem execução real.")

st.warning("Este módulo cria sandbox local, mas não executa recovery, rollback, git reset, force push ou shell.")


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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Sandbox", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar sandbox safe block"):
            run([
                "--mode", "sandbox",
                "--sandbox-mode", "safe_block",
                "--operator", "operator_k_os",
                "--reason", "operator_recovery_controlled_sandbox_safe_block"
            ])

    with c3:
        if st.button("Validar última"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Sandboxes", metrics.get("sandbox_record_count", 0))

        with m2:
            st.metric("Criadas local", metrics.get("sandbox_created_local_only_count", 0))

        with m3:
            st.metric("Bloqueadas", metrics.get("sandbox_blocked_by_governance_count", 0))

        with m4:
            st.metric("Recovery real", metrics.get("recovery_execution_count", 0))

        st.subheader("Sandboxes recentes")
        st.dataframe(report.get("recent_sandbox_records", []), use_container_width=True)

with tab2:
    sandbox_mode = st.selectbox("Sandbox mode", ["safe_block", "controlled_rehearsal", "audit_only"])
    operator = st.text_input("Operator", value="operator_k_os")
    reason = st.text_input("Reason", value="operator_recovery_controlled_sandbox")

    if st.button("Registrar sandbox", type="primary"):
        run([
            "--mode", "sandbox",
            "--sandbox-mode", sandbox_mode,
            "--operator", operator,
            "--reason", reason
        ])

    record = read_json(SANDBOX_PATH)
    if record:
        st.subheader("Última sandbox")
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