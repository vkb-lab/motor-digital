import streamlit as st

from k_atlas.kaizen.local_coworker import (
    process_bridge_inbox,
    get_latest_status,
    load_bridge_commands,
    load_state,
)

st.set_page_config(page_title="KOS Local Coworker", layout="wide")

st.title("K-OS Local Coworker")
st.caption("Coworker local para consumir comandos do Command Bridge. Seguro, local e sem Codex externo.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "LOCAL")
col2.metric("Autonomia", "TIER 1")
col3.metric("Repo write", "BLOQUEADO")
col4.metric("IA paga", "BLOQUEADA")

st.warning("Este coworker diagnostica e prepara tarefas. Ele nao altera codigo, nao executa shell arbitrario, nao faz commit, nao faz push, nao usa IA paga e nao publica.")

if st.button("Processar inbox agora", use_container_width=True):
    st.json(process_bridge_inbox(limit=10, execute_diagnostics=True))

latest = get_latest_status()
state = load_state()
commands = load_bridge_commands(limit=20)

st.subheader("Status")
st.json(latest)

st.subheader("Estado")
st.json(state)

st.subheader("Comandos vistos no Command Bridge")
for item in commands:
    with st.expander(f"{item.get('command_id')} - {item.get('title')}"):
        st.write("Prioridade:", item.get("priority"))
        st.write("Area:", item.get("area"))
        st.write("Fonte:", item.get("_source_path"))
        st.code(item.get("body", ""), language="text")