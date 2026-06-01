import json
from pathlib import Path
import streamlit as st

from k_atlas.launch_sandbox import run_launch_sandbox

st.set_page_config(page_title="KOS Client Launch Board", layout="wide")

st.title("KOS Client Launch Board")
st.caption("Board de canais e previews por cliente.")

if st.button("Gerar board demo", use_container_width=True):
    result = run_launch_sandbox()
    st.session_state["phase8_board"] = result["board"]

board = st.session_state.get("phase8_board")

if board:
    st.metric("Status", board["status"])
    st.metric("Cliente", board["client_id"])
    for card in board.get("cards", []):
        with st.container(border=True):
            st.write(f"**{card['title']}**")
            st.write(f"Status: `{card['status']}`")
            st.write(f"Acao real executada: `{card['real_action_executed']}`")
else:
    st.info("Gere o board demo.")
