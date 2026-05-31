from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RISK_SCRIPT = PROJECT_ROOT / "ops" / "k_os_ai_risk_classifier.py"
LICENSE_SCRIPT = PROJECT_ROOT / "ops" / "k_os_license_gate.py"
RISK_REPORT = PROJECT_ROOT / "reports" / "risk" / "latest_ai_risk_classifier_report.json"
LICENSE_REPORT = PROJECT_ROOT / "reports" / "license" / "latest_license_gate_report.json"

st.set_page_config(page_title="K-OS AI Risk Classifier", layout="wide")

st.title("K-OS AI Risk Classifier")
st.caption("Checkpoint 021 - classificador de risco, license gate e emergency kill switch seguro.")

st.warning(
    "Autodestrutivo no K-OS significa desativar, revogar, bloquear conectores e preservar auditoria. "
    "Apagar dados do cliente silenciosamente é bloqueado."
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


def run(cmd: list[str]) -> None:
    completed = subprocess.run(
        cmd,
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


tab1, tab2, tab3 = st.tabs(["Risk Classifier", "License Gate", "Relatórios"])

with tab1:
    st.header("Classificar ação")
    action = st.text_area("Ação", value="Vender agente por assinatura para cliente com kill switch de emergencia")
    agent = st.text_input("Agente", value="marketplace_ia_agent")
    target = st.text_input("Alvo", value="customer_license")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Classificar", type="primary"):
            run([python_exe(), str(RISK_SCRIPT), "--mode", "classify", "--action", action, "--agent", agent, "--target", target])
    with c2:
        if st.button("Smoke test risco"):
            run([python_exe(), str(RISK_SCRIPT), "--mode", "smoke-test"])
    with c3:
        if st.button("Scan policy"):
            run([python_exe(), str(RISK_SCRIPT), "--mode", "scan-policy"])

with tab2:
    st.header("License Gate")
    st.write("Licenças reais ficam locais em local_secrets/k_os_licenses/ e não vão para GitHub.")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Inicializar registry"):
            run([python_exe(), str(LICENSE_SCRIPT), "--mode", "init"])
    with c2:
        if st.button("Emitir demo local"):
            run([python_exe(), str(LICENSE_SCRIPT), "--mode", "issue-demo"])
    with c3:
        if st.button("Auditar licenças"):
            run([python_exe(), str(LICENSE_SCRIPT), "--mode", "audit"])

    reason = st.text_input("Motivo do lockdown", value="emergencia, falta de acordo ou risco contratual")
    if st.button("Emergency lockdown local", type="primary"):
        run([python_exe(), str(LICENSE_SCRIPT), "--mode", "lockdown", "--reason", reason])

with tab3:
    st.header("Últimos relatórios")

    if RISK_REPORT.exists():
        st.subheader("Risk")
        st.json(json.loads(RISK_REPORT.read_text(encoding="utf-8-sig")))
    else:
        st.info("Relatório de risco ainda não encontrado.")

    if LICENSE_REPORT.exists():
        st.subheader("License")
        st.json(json.loads(LICENSE_REPORT.read_text(encoding="utf-8-sig")))
    else:
        st.info("Relatório de licença ainda não encontrado.")

st.caption("K-OS 021 - risco, permissão comercial, assinatura e emergency kill switch seguro.")