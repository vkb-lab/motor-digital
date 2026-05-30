from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autonomy_audit_monitor.monitor import AutonomyAuditMonitor

st.set_page_config(page_title="K-Atlas Autonomy Audit", layout="wide")
st.title("K-Atlas Autonomy Audit Monitor")
st.caption("Audita a fila para garantir que nao ha execucao automatica indevida.")

monitor = AutonomyAuditMonitor()
if st.button("Rodar auditoria", type="primary"):
    st.json(monitor.audit())
