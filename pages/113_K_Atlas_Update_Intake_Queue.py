from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.update_intake_queue.queue import UpdateIntakeQueue

st.set_page_config(page_title="K-Atlas Update Intake Queue", layout="wide")
st.title("K-Atlas Update Intake Queue")
st.caption("Fila de entrada para updates locais supervisionados.")

queue = UpdateIntakeQueue()\nif st.button("Adicionar update demo"):\n    st.json(queue.enqueue({"installer_name": "K_ATLAS_DEMO_UPDATE.ps1"}))\nst.json(queue.build_report())
