from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_security_firewall.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "security" / "latest_security_firewall_report.json"

st.set_page_config(page_title="K-OS Security Firewall", layout="wide")

st.title("K-OS Security Firewall")
st.caption("Checkpoint 015 - pre-commit guard, secrets scanner e auditoria de segurança.")

st.warning(
    "Este módulo bloqueia commit de tokens, credenciais, leads, pacotes manuais e dados sensíveis. "
    "Ações externas continuam bloqueadas por padrão."
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


def run_mode(mode: str):
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), "--mode", mode],
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
        st.error(f"Bloqueado ou falhou. Código: {completed.returncode}")


col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Scan working tree"):
        run_mode("scan-working")

with col2:
    if st.button("Scan staged"):
        run_mode("scan-staged")

with col3:
    if st.button("Instalar pre-commit hook"):
        run_mode("install-hook")

with col4:
    if st.button("Smoke test"):
        run_mode("smoke-test")

st.divider()

st.header("Último relatório")

if REPORT_PATH.exists():
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Status", report.get("status", "N/A"))

    with c2:
        st.metric("OK", str(report.get("ok")))

    with c3:
        st.metric("Findings", report.get("findings_count", 0))

    with c4:
        st.metric("Bloqueantes", report.get("blocking_findings_count", 0))

    st.json(report)

else:
    st.info("Nenhum relatório encontrado ainda.")

st.divider()

st.header("Política")

st.write("- live/ não deve ir para GitHub")
st.write("- tokens e credenciais são bloqueados")
st.write("- leads e pacotes manuais são bloqueados")
st.write("- publicação externa continua bloqueada")
st.write("- aprovação humana continua obrigatória")

st.caption("K-OS 015 - segurança antes de expansão multimodal, APIs e automações reais.")