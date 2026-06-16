import json
from pathlib import Path
import streamlit as st

ROOT = Path.cwd()
STATE = ROOT / "memory" / "kaizen" / "state.json"
REPORT = ROOT / "reports" / "KOS_KAIZEN_LAST_CYCLE_REPORT.json"
QUEUE = ROOT / "memory" / "kaizen" / "task_queue.json"

st.set_page_config(page_title="KOS Kaizen 24/7", layout="wide")
st.title("KOS Kaizen 24/7 Orchestrator")
st.caption("Modo seguro: observa, planeja e registra. Nao publica e nao chama API paga.")

def load(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {}

col1, col2, col3 = st.columns(3)

state = load(STATE)
report = load(REPORT)
queue = load(QUEUE)

col1.metric("Status", state.get("status", "N/A"))
col2.metric("Modo", state.get("mode", "N/A"))
col3.metric("Ciclos", state.get("cycles", 0))

st.subheader("Ultimo ciclo")
st.json(report)

st.subheader("Fila")
st.json(queue)
