from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.update_apply_runner.runner import UpdateApplyRunner

st.set_page_config(page_title="K-Atlas Update Apply Runner", layout="wide")
st.title("K-Atlas Update Apply Runner")
st.caption("Runner supervisionado. Nao executa automaticamente.")

runner = UpdateApplyRunner()\nst.json(runner.dry_run())\nif st.button("Registrar ready para apply supervisionado"):\n    st.json(runner.record_supervised_apply_ready())
