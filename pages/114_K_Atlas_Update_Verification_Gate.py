from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.update_verification_gate.gate import UpdateVerificationGate

st.set_page_config(page_title="K-Atlas Update Verification Gate", layout="wide")
st.title("K-Atlas Update Verification Gate")
st.caption("Gate de verificacao para updates locais.")

gate = UpdateVerificationGate()\nif st.button("Verificar fila"):\n    st.json(gate.build_verified_queue())
