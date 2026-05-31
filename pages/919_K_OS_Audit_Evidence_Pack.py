from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_audit_evidence_pack.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "audit" / "latest_audit_evidence_pack.json"
MD_PATH = PROJECT_ROOT / "reports" / "audit" / "latest_audit_evidence_pack.md"
CHECKLIST_PATH = PROJECT_ROOT / "reports" / "audit" / "latest_audit_checklist.md"

st.set_page_config(page_title="K-OS Audit Evidence Pack", layout="wide")

st.title("K-OS Audit Evidence Pack")
st.caption("Checkpoint 019 - pacote de evidências para auditoria, conselho e avaliação enterprise.")

st.warning(
    "Este pacote é readiness interno. Não declarar SOC 2, ISO 27001, LGPD ou GDPR como certificação formal sem auditor externo."
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


def run_generate() -> None:
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
        st.success("Pacote gerado.")
    else:
        st.error(f"Falhou: {completed.returncode}")


if st.button("Gerar pacote de auditoria", type="primary"):
    run_generate()

st.divider()

if REPORT_PATH.exists():
    pack = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

    readiness = pack.get("readiness", {})

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Status", pack.get("status", "N/A"))

    with c2:
        st.metric("Score", str(readiness.get("score", 0)) + "%")

    with c3:
        st.metric("Controles OK", f"{readiness.get('control_ok', 0)}/{readiness.get('control_total', 0)}")

    with c4:
        st.metric("Checkpoints OK", f"{readiness.get('checkpoint_ok', 0)}/{readiness.get('checkpoint_total', 0)}")

    st.header("Security Position")
    st.json(pack.get("security_position", {}))

    st.header("Checkpoint Evidence")
    st.json(pack.get("checkpoint_evidence", []))

    st.header("Control Evidence")
    st.json(pack.get("control_evidence", []))

    st.header("Known Gaps")
    st.json(pack.get("known_gaps", []))

else:
    st.info("Nenhum pacote gerado ainda.")

st.divider()

tab1, tab2 = st.tabs(["Relatório Markdown", "Checklist"])

with tab1:
    if MD_PATH.exists():
        st.code(MD_PATH.read_text(encoding="utf-8-sig"), language="markdown")
    else:
        st.info("Relatório Markdown ainda não encontrado.")

with tab2:
    if CHECKLIST_PATH.exists():
        st.code(CHECKLIST_PATH.read_text(encoding="utf-8-sig"), language="markdown")
    else:
        st.info("Checklist ainda não encontrado.")

st.caption("K-OS 019 - evidência antes de escala, API externa e operação enterprise.")