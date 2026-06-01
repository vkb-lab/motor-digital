from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_rollback_manual_stub_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "rollback_manual_stub" / "latest_agent_rollback_manual_stub_report.json"
STUB_PATH = PROJECT_ROOT / "reports" / "rollback_manual_stub" / "latest_rollback_manual_stub_record.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "rollback_manual_stub" / "latest_rollback_manual_stub_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "rollback_manual_stub" / "k_os_agent_rollback_manual_stub_policy.json"

st.set_page_config(page_title="K-OS Rollback Manual Stub", layout="wide")

st.title("K-OS Agent Rollback Manual Execution Stub Core")
st.caption("Checkpoint 057 - stub manual sem execução real.")

st.warning("Este módulo registra intenção, mas não executa rollback real, não apaga dados, não roda git reset e não altera arquivos.")


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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Stub manual", "Validação", "Policy"])

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
            st.metric("Registros", metrics.get("manual_stub_record_count", 0))

        with m2:
            st.metric("Intenção bloqueada", metrics.get("intent_blocked_count", 0))

        with m3:
            st.metric("Intenção registrada", metrics.get("intent_recorded_blocked_count", 0))

        with m4:
            st.metric("Rollback real", metrics.get("rollback_execution_count", 0))

        st.subheader("Registros recentes")
        st.dataframe(report.get("recent_manual_stub_records", []), use_container_width=True)

with tab2:
    stub_mode = st.selectbox("Stub mode", ["block_intent", "record_intent", "revoke_intent"])
    operator = st.text_input("Operator", value="operator_k_os")
    intent = st.text_input("Intent", value="manual rollback intent - blocked by design")
    reason = st.text_input("Reason", value="operator_manual_stub_test")

    if st.button("Registrar stub", type="primary"):
        run([
            "--mode", "stub",
            "--stub-mode", stub_mode,
            "--operator", operator,
            "--intent", intent,
            "--reason", reason
        ])

    stub = read_json(STUB_PATH)
    if stub:
        st.subheader("Último stub")
        st.json(stub)

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