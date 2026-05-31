from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_incident_lockdown_quarantine_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "incident_lockdown" / "latest_agent_incident_lockdown_report.json"
INCIDENT_PATH = PROJECT_ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_record.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "incident_lockdown" / "latest_incident_lockdown_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "incident_lockdown" / "k_os_agent_incident_lockdown_policy.json"

st.set_page_config(page_title="K-OS Incident Lockdown", layout="wide")

st.title("K-OS Agent Incident Lockdown and Quarantine Core")
st.caption("Checkpoint 052 - bloqueio local, quarentena e congelamento de evidências.")

st.warning(
    "Lockdown seguro: não apaga dados, não executa ações reais e exige revisão humana para liberação."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Lockdown", "Validação", "Policy"])

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
            st.metric("Incidentes", metrics.get("incident_count", 0))

        with m2:
            st.metric("Quarentena ativa", metrics.get("active_quarantine_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Delete data", metrics.get("data_delete_count", 0))

        st.subheader("Incidentes recentes")
        st.dataframe(report.get("recent_incidents", []), use_container_width=True)

with tab2:
    scope = st.text_input("Scope", value="agent_execution_chain")
    severity = st.selectbox("Severity", ["SEV1", "SEV2", "SEV3", "SEV4"], index=2)
    reason = st.text_input("Reason", value="operator_incident_lockdown_test")
    operator = st.text_input("Operator", value="operator_k_os")

    if st.button("Criar lockdown/quarentena", type="primary"):
        run([
            "--mode", "lockdown",
            "--scope", scope,
            "--severity", severity,
            "--reason", reason,
            "--operator", operator
        ])

    incident = read_json(INCIDENT_PATH)
    if incident:
        st.subheader("Último incidente")
        st.json(incident)

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