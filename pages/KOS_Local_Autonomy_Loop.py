import streamlit as st

from k_atlas.kaizen.local_autonomy_loop import (
    run_local_autonomy_cycle,
    get_latest_local_autonomy_loop_status,
)

st.set_page_config(page_title="KOS Local Autonomy Loop", layout="wide")

st.title("K-OS Local Autonomy Loop")
st.caption("Orquestra Bridge -> Coworker -> Patch Workspace -> Command Composer. Nao executa comandos.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "LOCAL")
col2.metric("Autonomia", "TIER 4")
col3.metric("Execucao", "BLOQUEADA")
col4.metric("Repo write", "BLOQUEADO")

st.warning("Este loop prepara tarefas e comandos. Ele nao aplica patches, nao altera repo, nao faz commit, nao faz push, nao usa IA paga e nao publica.")

if st.button("Rodar ciclo agora", use_container_width=True):
    st.json(run_local_autonomy_cycle(command_limit=10))

latest = get_latest_local_autonomy_loop_status()

st.subheader("Status do loop")
st.json(latest)

st.subheader("Como ligar o loop local")
st.code('powershell -ExecutionPolicy Bypass -File scripts\\start_kos_local_autonomy_loop.ps1', language="powershell")