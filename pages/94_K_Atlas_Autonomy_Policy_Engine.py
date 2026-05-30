from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autonomy_policy_engine.policy import AutonomyPolicyEngine

st.set_page_config(page_title="K-Atlas Autonomy Policy", layout="wide")
st.title("K-Atlas Autonomy Policy Engine")
st.caption("Politica de autonomia supervisionada. Nao executa acoes reais.")

engine = AutonomyPolicyEngine()
mode = st.selectbox("Modo", ["observe", "plan", "recommend", "queue"], index=0)
if st.button("Avaliar politica", type="primary"):
    st.json(engine.evaluate({"mode": mode, "risk_level": "low"}))
