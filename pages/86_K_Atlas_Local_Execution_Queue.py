from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_execution_queue.queue import LocalExecutionQueue

st.set_page_config(page_title="K-Atlas Execution Queue", layout="wide")
st.title("K-Atlas Local Execution Queue")
st.caption("Fila de execucao assistida. Espera aprovacao humana.")

queue = LocalExecutionQueue()

if st.button("Enfileirar ultima rota pronta", type="primary"):
    st.json(queue.enqueue_latest_ready_route())

st.divider()
st.json(queue.summary())
