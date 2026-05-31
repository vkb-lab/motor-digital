from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_enterprise_readiness_report.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "enterprise" / "latest_enterprise_readiness_report.json"
MD_PATH = PROJECT_ROOT / "reports" / "enterprise" / "latest_enterprise_readiness_report.md"
DD_PATH = PROJECT_ROOT / "reports" / "enterprise" / "latest_enterprise_due_diligence_pack.md"

st.set_page_config(page_title="K-OS Enterprise Readiness", layout="wide")

st.title("K-OS Enterprise Readiness Report")
st.caption("Checkpoint 023 - pacote executivo de maturidade enterprise.")

st.warning(
    "Este painel nao declara certificacao formal. SOC 2, ISO 27001, LGPD e GDPR exigem auditoria externa competente."
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
        st.success("Relatorio enterprise atualizado.")
    else:
        st.error(f"Falhou: {completed.returncode}")


if st.button("Gerar Enterprise Readiness Report", type="primary"):
    generate()

st.divider()

if REPORT_PATH.exists():
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("OK", str(report.get("ok")))

    with c2:
        st.metric("Score", str(report.get("enterprise_readiness_score")) + "%")

    with c3:
        st.metric("Maturidade", report.get("maturity_level", "N/A"))

    with c4:
        st.metric("Controles", f"{report.get('controls_passed')}/{report.get('controls_total')}")

    with c5:
        st.metric("Blockers", len(report.get("operational_blockers", [])))

    st.header("Resumo executivo")
    st.success(report.get("statement", {}).get("safe_claim", ""))

    st.error(report.get("statement", {}).get("restricted_claim", ""))

    st.header("Matriz de controles")
    st.dataframe(report.get("controls", []), use_container_width=True)

    st.header("Gaps conhecidos")
    for gap in report.get("known_gaps", []):
        st.write("- " + gap)

    st.header("Blockers operacionais")
    if report.get("operational_blockers"):
        st.json(report.get("operational_blockers"))
    else:
        st.success("Nenhum blocker operacional encontrado.")

    st.header("Acoes recomendadas")
    for action in report.get("recommended_actions", []):
        st.write("- " + action)

else:
    st.info("Relatorio ainda nao encontrado.")

st.divider()

if MD_PATH.exists():
    st.header("Relatorio Markdown")
    st.code(MD_PATH.read_text(encoding="utf-8-sig"), language="markdown")

if DD_PATH.exists():
    st.header("Due Diligence Pack")
    st.code(DD_PATH.read_text(encoding="utf-8-sig"), language="markdown")