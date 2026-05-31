from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_legal_commercial_templates.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "legal" / "latest_legal_commercial_templates_report.json"
MD_PATH = PROJECT_ROOT / "reports" / "legal" / "latest_legal_commercial_templates_report.md"
TEMPLATE_DIR = PROJECT_ROOT / "reports" / "legal" / "templates"

st.set_page_config(page_title="K-OS Legal Commercial Templates", layout="wide")

st.title("K-OS Legal Commercial License Templates")
st.caption("Checkpoint 025 - templates comerciais para venda, assinatura, licenca, SLA e revogacao segura.")

st.warning(
    "Templates operacionais. Nao usar como contrato final sem revisao juridica, revisao comercial e adequacao ao caso concreto."
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


def generate() -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), "--mode", "generate"],
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
        st.success("Templates atualizados.")
    else:
        st.error(f"Falhou: {completed.returncode}")


if st.button("Gerar templates comerciais", type="primary"):
    generate()

st.divider()

if REPORT_PATH.exists():
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("OK", str(report.get("ok")))

    with c2:
        st.metric("Templates", report.get("templates_generated"))

    with c3:
        st.metric("Prereqs", f"{report.get('prerequisites_ok')}/{report.get('prerequisites_total')}")

    with c4:
        st.metric("Blockers", len(report.get("blockers", [])))

    st.header("Resumo")
    st.success(report.get("safe_claim", ""))
    st.error(report.get("restricted_claim", ""))

    st.header("Gates obrigatorios")
    for gate in report.get("required_gates_before_customer_activation", []):
        st.write("- " + gate)

    st.header("Templates")
    for item in report.get("template_files", []):
        path = PROJECT_ROOT / item.get("path")
        with st.expander(item.get("filename"), expanded=False):
            if path.exists():
                st.code(path.read_text(encoding="utf-8-sig"), language="markdown")
            else:
                st.info("Arquivo nao encontrado.")

    st.header("Blockers")
    if report.get("blockers"):
        st.json(report.get("blockers"))
    else:
        st.success("Nenhum blocker operacional encontrado.")

else:
    st.info("Relatorio ainda nao encontrado.")

if MD_PATH.exists():
    st.divider()
    st.header("Relatorio Markdown")
    st.code(MD_PATH.read_text(encoding="utf-8-sig"), language="markdown")