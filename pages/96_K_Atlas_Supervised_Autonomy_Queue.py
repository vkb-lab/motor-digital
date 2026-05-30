from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.supervised_autonomy_queue.queue import SupervisedAutonomyQueue

st.set_page_config(page_title="K-Atlas Supervised Autonomy Queue", layout="wide")
st.title("K-Atlas Supervised Autonomy Queue")
st.caption("Fila de autonomia supervisionada aguardando aprovacao humana.")

queue = SupervisedAutonomyQueue()
if st.button("Construir fila", type="primary"):
    st.json(queue.build_queue())
st.divider()
st.json(queue.summary())
