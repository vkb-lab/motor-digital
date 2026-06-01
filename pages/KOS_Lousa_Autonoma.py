import streamlit as st
from pathlib import Path
from k_atlas.command_autopilot import run_autopilot_demo
from k_atlas.whiteboard.board_store import load_board

st.set_page_config(page_title="Lousa Autonoma K-OS", layout="wide")

st.title("Lousa Autonoma K-OS")
st.caption("Cards operacionais por job, agente e status")

if st.button("Gerar lousa demo", use_container_width=True):
    run_autopilot_demo()
    st.success("Lousa demo gerada.")

board = load_board()

st.subheader("Estado da lousa")
st.json(board)

cards = board.get("cards", [])

if cards:
    st.subheader("Cards")
    for card in cards:
        with st.container(border=True):
            st.write(f"**{card.get('title', card.get('task_id'))}**")
            st.write(f"Agente: `{card.get('agent')}`")
            st.write(f"Status: `{card.get('status')}`")
            st.write(f"Aprovacao requerida: `{card.get('approval_required', True)}`")
else:
    st.info("Nenhum card carregado ainda. Gere a lousa demo.")
