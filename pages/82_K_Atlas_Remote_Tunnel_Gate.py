from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.remote_tunnel_gate.gate import RemoteTunnelGate

st.set_page_config(page_title="K-Atlas Remote Tunnel Gate", layout="wide")
st.title("K-Atlas Remote Tunnel Gate")
st.caption("Gate de readiness remoto. Nao inicia tunel e nao armazena token.")

gate = RemoteTunnelGate()
summary = gate.summary()
metrics = summary.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Fila", metrics.get("tunnel_queue_total", 0))
with c2:
    st.metric("Aguardando", metrics.get("waiting_human_remote_review", 0))
with c3:
    st.metric("Tunel iniciado", str(metrics.get("tunnel_started")))
with c4:
    st.metric("Token salvo", str(metrics.get("token_stored")))

st.divider()
provider = st.selectbox("Provider planejado", ["manual", "tailscale", "cloudflare", "ngrok", "vpn"])
if st.button("Criar pedido de readiness remoto"):
    st.json(gate.create_request({"provider": provider, "start_tunnel": False, "public_exposure": False, "store_token": False}))

st.subheader("Fila")
st.json(gate.load_queue())
