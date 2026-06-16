import streamlit as st
from pathlib import Path
import json

from k_atlas.kaizen.local_command_composer import (
    create_command_drafts_from_work_orders,
    get_latest_command_composer_status,
    load_existing_command_drafts,
)

st.set_page_config(page_title="KOS Local Command Composer", layout="wide")

st.title("K-OS Local Command Composer")
st.caption("Transforma work orders em comandos PowerShell revisaveis. Nao executa.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "LOCAL")
col2.metric("Autonomia", "TIER 3")
col3.metric("Execucao", "BLOQUEADA")
col4.metric("Repo write", "BLOQUEADO")

st.warning("Este composer gera comandos locais em local_runtime. Ele nao executa comandos, nao altera repo, nao faz commit, nao faz push, nao usa IA paga e nao publica.")

if st.button("Gerar command drafts agora", use_container_width=True):
    st.json(create_command_drafts_from_work_orders(limit=10))

latest = get_latest_command_composer_status()
drafts = load_existing_command_drafts(limit=20)

st.subheader("Status")
st.json(latest)

st.subheader("Command drafts")
if not drafts:
    st.info("Nenhum command draft local ainda.")
else:
    for draft in drafts:
        label = f"{draft.get('draft_id')} - {draft.get('title')} - risco {draft.get('risk')}"
        with st.expander(label):
            st.write("Work order:", draft.get("source_work_order_id"))
            st.write("Task type:", draft.get("task_type"))
            st.subheader("PowerShell")
            st.code(draft.get("powershell_command", ""), language="powershell")
            st.subheader("Gates")
            st.json(draft.get("gates", {}))