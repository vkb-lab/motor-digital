from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.lan_cockpit_access.lan import LANCockpitAccess

st.set_page_config(page_title="K-Atlas LAN Access", layout="wide")
st.title("K-Atlas LAN Cockpit Access")
st.caption("Planejamento de acesso LAN. Nao abre firewall nem servidor automaticamente.")

lan = LANCockpitAccess()
report = lan.build_plan({"mode": "readiness", "port": 8506})
net = report.get("network", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Local IP", net.get("local_ip"))
with c2:
    st.metric("Porta", net.get("port"))
with c3:
    st.metric("Firewall", str(report.get("firewall_changed")))
with c4:
    st.metric("Servidor iniciado", str(report.get("server_started")))

st.divider()
st.code(net.get("recommended_url", ""), language="text")
st.json(report)
