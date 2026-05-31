from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_replay_forensics_viewer_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "replay_forensics" / "latest_agent_replay_forensics_report.json"
BUNDLE_PATH = PROJECT_ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_bundle.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "replay_forensics" / "latest_replay_forensics_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "replay_forensics" / "k_os_agent_replay_forensics_policy.json"

st.set_page_config(page_title="K-OS Replay Forensics", layout="wide")

st.title("K-OS Agent Replay and Forensics Viewer Core")
st.caption("Checkpoint 051 - replay visual, forensics e timeline auditavel sem executar ações.")

st.warning(
    "Viewer local read-only. Replay não executa ações, não envia dados externos e não revela payload bruto."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Forensics", "Timeline", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Gerar bundle"):
            run(["--mode", "bundle", "--reason", "operator_forensics_bundle"])

    with c3:
        if st.button("Validar bundle"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Bundles", metrics.get("forensics_bundle_count", 0))

        with m2:
            st.metric("Validados", metrics.get("validated_count", 0))

        with m3:
            st.metric("Bloqueados", metrics.get("blocked_count", 0))

        with m4:
            st.metric("Replay exec", metrics.get("replay_execution_count", 0))

        st.subheader("Bundles recentes")
        st.dataframe(report.get("recent_bundles", []), use_container_width=True)

with tab2:
    bundle = read_json(BUNDLE_PATH)
    validation = read_json(VALIDATION_PATH)

    if bundle:
        st.subheader("Bundle")
        st.json(bundle)

    if validation:
        st.subheader("Validação")
        st.json(validation)

with tab3:
    bundle = read_json(BUNDLE_PATH)

    if bundle and bundle.get("timeline"):
        st.dataframe(bundle.get("timeline", []), use_container_width=True)
    else:
        st.info("Nenhuma timeline gerada.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")