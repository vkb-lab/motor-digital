from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_schema_guard.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "schema" / "latest_schema_guard_report.json"

st.set_page_config(page_title="K-OS Schema Guard", layout="wide")

st.title("K-OS Schema Guard")
st.caption("Checkpoint 016 - validação estrutural de JSONs operacionais.")

st.warning(
    "Este módulo valida diagnósticos, propostas, leads e gates antes do uso operacional. "
    "Nenhuma API externa é chamada."
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
        st.error(f"Bloqueado ou falhou. Código: {completed.returncode}")


col1, col2 = st.columns(2)

with col1:
    if st.button("Smoke test"):
        run(["--mode", "smoke-test"])

with col2:
    if st.button("Scan local"):
        run(["--mode", "scan-local"])

st.divider()

st.header("Validar arquivo específico")

file_path = st.text_input(
    "Caminho relativo",
    value="content_packs/marketplace_ia/instagram_posts_v2.json",
)

schema = st.selectbox(
    "Schema",
    [
        "",
        "lead_v1",
        "public_capture_v1",
        "diagnostic_v1",
        "proposal_v1",
        "gate_decision_v1",
        "instagram_posts_v1",
        "generic_json_v1",
    ],
)

if st.button("Validar arquivo"):
    args = ["--mode", "validate-file", "--path", file_path]
    if schema:
        args.extend(["--schema", schema])
    run(args)

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
        st.metric("Erros", report.get("errors_count", 0))

    with c4:
        st.metric("Bloqueantes", report.get("blocking_errors_count", 0))

    st.json(report)
else:
    st.info("Nenhum relatório encontrado ainda.")

st.caption("K-OS 016 - Structured validation antes de Recovery Engine, gates e multimodal.")