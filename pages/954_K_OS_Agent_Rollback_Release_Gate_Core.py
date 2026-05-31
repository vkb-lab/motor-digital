from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_rollback_release_gate_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "rollback_release_gate" / "latest_agent_rollback_release_gate_report.json"
RELEASE_PATH = PROJECT_ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_record.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "rollback_release_gate" / "latest_rollback_release_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "rollback_release_gate" / "k_os_agent_rollback_release_gate_policy.json"

st.set_page_config(page_title="K-OS Rollback Release Gate", layout="wide")

st.title("K-OS Agent Rollback Approval and Release Gate Core")
st.caption("Checkpoint 054 - gate de aprovacao/bloqueio para rollback futuro.")

st.warning("Este gate não executa rollback real, não apaga dados e não altera arquivos.")


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
            st.metric("Registros", metrics.get("release_record_count", 0))

        with m2:
            st.metric("Aprovados", metrics.get("approved_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Execuções rollback", metrics.get("rollback_execution_count", 0))

        st.subheader("Registros recentes")
        st.dataframe(report.get("recent_release_records", []), use_container_width=True)

with tab2:
    decision = st.selectbox("Decision", ["block_future_rollback", "approve_future_rollback", "revoke_future_rollback"])
    operator = st.text_input("Operator", value="operator_k_os")
    reason = st.text_input("Reason", value="operator_rollback_release_gate_decision")

    if st.button("Registrar decisão", type="primary"):
        run(["--mode", "decide", "--decision", decision, "--operator", operator, "--reason", reason])

    release = read_json(RELEASE_PATH)
    if release:
        st.subheader("Último registro")
        st.json(release)

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