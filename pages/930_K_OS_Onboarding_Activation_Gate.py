from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_onboarding_activation_gate.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "onboarding" / "latest_onboarding_activation_report.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "onboarding" / "latest_activation_gate_validation.json"
PACKAGE_PATH = PROJECT_ROOT / "reports" / "onboarding" / "latest_onboarding_package.md"
POLICY_PATH = PROJECT_ROOT / "config" / "onboarding" / "k_os_onboarding_activation_policy.json"

st.set_page_config(page_title="K-OS Onboarding Activation Gate", layout="wide")

st.title("K-OS Onboarding and Activation Gate")
st.caption("Checkpoint 030 - validação final antes de ativar cliente/agente.")

st.warning(
    "Este painel não ativa cliente de verdade. Ele só valida gates, gera blockers e cria pacote de onboarding."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Validar cliente", "Pacote", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Onboarding Gate", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo local"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar onboarding"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Cases", metrics.get("onboarding_case_count", 0))

        with m2:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m3:
            st.metric("Prontos para revisão", metrics.get("ready_for_review_count", 0))

        with m4:
            st.metric("Ativação real", str(report.get("real_customer_activation_enabled", False)))

        st.subheader("Onboarding cases")
        st.dataframe(report.get("cases", []), use_container_width=True)

        st.subheader("Foundation")
        st.dataframe(report.get("foundation", []), use_container_width=True)

with tab2:
    customer_alias = st.text_input("Customer alias", value="demo_customer")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Validar activation gate", type="primary"):
            run(["--mode", "validate", "--customer-alias", customer_alias])

    with col2:
        if st.button("Criar onboarding case"):
            run(["--mode", "create-case", "--customer-alias", customer_alias])

    if VALIDATION_PATH.exists():
        st.subheader("Última validação")
        validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8-sig"))

        v1, v2, v3 = st.columns(3)
        with v1:
            st.metric("Decision", validation.get("activation_decision", "N/A"))
        with v2:
            st.metric("Manual allowed", str(validation.get("manual_activation_allowed", False)))
        with v3:
            st.metric("Blockers", len(validation.get("blockers", [])))

        st.json(validation)

with tab3:
    if PACKAGE_PATH.exists():
        st.code(PACKAGE_PATH.read_text(encoding="utf-8-sig"), language="markdown")
    else:
        st.info("Pacote ainda não gerado.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")