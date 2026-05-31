from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_execution_result_ledger_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "execution_result_ledger" / "latest_agent_execution_result_ledger_report.json"
RECORD_PATH = PROJECT_ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_record.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "execution_result_ledger" / "latest_execution_result_ledger_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "execution_result_ledger" / "k_os_agent_execution_result_ledger_policy.json"

st.set_page_config(page_title="K-OS Execution Result Ledger", layout="wide")

st.title("K-OS Agent Execution Result Ledger Core")
st.caption("Checkpoint 050 - ledger auditável de resultados de execução allowlisted.")

st.warning(
    "Ledger local append-only. Não registra payload bruto nem token de aprovação em relatórios."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Registrar", "Validação", "Policy"])

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
            st.metric("Registros", metrics.get("ledger_record_count", 0))

        with m2:
            st.metric("Validados", metrics.get("validated_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Raw payload", metrics.get("raw_payload_record_count", 0))

        st.subheader("Registros recentes")
        st.dataframe(report.get("recent_records", []), use_container_width=True)

with tab2:
    reason = st.text_input("Reason", value="operator_execution_result_record")

    if st.button("Registrar resultado no ledger", type="primary"):
        run(["--mode", "record", "--reason", reason])

    record = read_json(RECORD_PATH)
    if record:
        st.subheader("Último registro")
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