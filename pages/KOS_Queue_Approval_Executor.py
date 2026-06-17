from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path.cwd()
BASE = ROOT / "local_runtime" / "kos_engineer_handoff"
STATUS = BASE / "latest_queue_approval_executor_status.json"
APPROVALS = BASE / "approvals"
EXECUTED = BASE / "executed"
FAILED = BASE / "failed"

st.set_page_config(page_title="KOS Queue Approval Executor", layout="wide")
st.title("K-OS Queue Approval Executor")
st.caption("Fase 66C — execução local governada por approvals JSON.")

cols = st.columns(4)
cols[0].metric("Approvals pendentes", len(list(APPROVALS.glob("*.json"))) if APPROVALS.exists() else 0)
cols[1].metric("Executados", len(list(EXECUTED.glob("*.json"))) if EXECUTED.exists() else 0)
cols[2].metric("Falhas", len(list(FAILED.glob("*.json"))) if FAILED.exists() else 0)
cols[3].metric("Browser automation", "bloqueada")

if STATUS.exists():
    st.subheader("Status")
    st.json(json.loads(STATUS.read_text(encoding="utf-8")))
else:
    st.info("Nenhum status ainda. Execute scripts/run_phase66c_queue_approval_executor.py.")

st.subheader("Approvals pendentes")
if APPROVALS.exists():
    for item in sorted(APPROVALS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]:
        st.code(str(item))
else:
    st.write("Diretório ainda não criado.")
