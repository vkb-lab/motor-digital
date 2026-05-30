from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.update_rollback_hook.hook import UpdateRollbackHook

st.set_page_config(page_title="K-Atlas Update Rollback Hook", layout="wide")
st.title("K-Atlas Update Rollback Hook")
st.caption("Hook de rollback para updates supervisionados.")

hook = UpdateRollbackHook()\nif st.button("Criar rollback hook"):\n    st.json(hook.create_hook())\nst.json(hook.load_hooks())
