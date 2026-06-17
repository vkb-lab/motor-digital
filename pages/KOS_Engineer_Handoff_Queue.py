
import streamlit as st

from k_atlas.kaizen.engineer_handoff_queue import (
    process_engineer_handoff_queue,
    get_engineer_handoff_queue_status,
    write_orchestrator_inbox_command,
)

st.set_page_config(page_title="KOS Engineer Handoff Queue", layout="wide")

st.title("K-OS Engineer Handoff Queue")
st.caption("Fila para o orquestrador enviar comandos sem clicar na UI.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Modo", "QUEUE")
c2.metric("Click UI", "NAO")
c3.metric("Duplicate Guard", "ATIVO")
c4.metric("Execucao", "GATED")

st.warning("O orquestrador escreve no inbox. O K-OS valida e stageia. Execucao continua exigindo confirmacao humana.")

if st.button("Processar inbox agora", use_container_width=True):
    st.json(process_engineer_handoff_queue(limit=20))

st.subheader("Enviar comando para inbox")
title = st.text_input("Titulo", value="engineer_command")
command = st.text_area("Comando PowerShell", height=220)

if st.button("Escrever no inbox", use_container_width=True):
    st.json(write_orchestrator_inbox_command(command, title=title))

st.subheader("Status")
st.json(get_engineer_handoff_queue_status())
