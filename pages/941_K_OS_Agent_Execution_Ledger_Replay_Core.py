from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_execution_ledger_replay_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "agent_ledger" / "latest_agent_execution_ledger_report.json"
SNAPSHOT_PATH = PROJECT_ROOT / "reports" / "agent_ledger" / "latest_agent_execution_evidence_snapshot.json"
REPLAY_PATH = PROJECT_ROOT / "reports" / "agent_ledger" / "latest_agent_execution_replay_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "agent_ledger" / "k_os_agent_execution_ledger_replay_policy.json"

st.set_page_config(page_title="K-OS Agent Execution Ledger", layout="wide")

st.title("K-OS Agent Execution Ledger and Replay")
st.caption("Checkpoint 041 - ledger auditável, evidência, hashes e replay controlado.")

st.warning(
    "Ledger local. Replay real exige approval. Dry-run é o padrão. Estado bruto fica fora do GitHub."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Replay", "Evidência", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar ledger", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Registrar última execução"):
            run(["--mode", "record-latest", "--reason", "operator_record_latest"])

    with c3:
        if st.button("Auditar ledger"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Entradas", metrics.get("ledger_entry_count", 0))

        with m2:
            st.metric("Replays", metrics.get("replay_count", 0))

        with m3:
            st.metric("Dry-runs", metrics.get("dry_run_entry_count", 0))

        with m4:
            st.metric("Executadas", metrics.get("executed_entry_count", 0))

        with m5:
            st.metric("Falhas", metrics.get("failed_entry_count", 0))

        st.subheader("Entradas do ledger")
        st.dataframe(report.get("entries", []), use_container_width=True)

        st.subheader("Replays recentes")
        st.dataframe(report.get("recent_replays", []), use_container_width=True)

with tab2:
    ledger_id = st.text_input("Ledger ID")
    reason = st.text_input("Motivo", value="operator_replay_review")
    approved = st.checkbox("Approval humano registrado")
    execute = st.checkbox("Executar de verdade, não apenas dry-run")

    args = ["--mode", "replay", "--ledger-id", ledger_id, "--reason", reason]

    if approved:
        args.append("--approved")

    if execute:
        args.append("--execute")

    if st.button("Rodar replay controlado", type="primary"):
        run(args)

    replay = read_json(REPLAY_PATH)
    if replay:
        st.subheader("Último replay")
        st.json(replay)

with tab3:
    snapshot = read_json(SNAPSHOT_PATH)

    if snapshot:
        st.json(snapshot)
    else:
        st.info("Snapshot ainda não gerado.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")