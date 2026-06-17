
import streamlit as st

from k_atlas.kaizen.engineer_handoff_bridge import (
    build_engineer_prompt_from_review,
    stage_engineer_response,
    get_engineer_handoff_status,
    list_staged_engineer_commands,
    CONFIRMATION_PHRASE,
)

st.set_page_config(page_title="KOS Engineer Handoff Bridge", layout="wide")

st.title("K-OS Engineer Handoff Bridge")
st.caption("Ponte local entre K-OS Coworker e K-Atlas Engineer.")

status = get_engineer_handoff_status()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bridge", "ATIVO")
c2.metric("Staged", status.get("staged_commands_count", 0))
c3.metric("Execucao", "GATED")
c4.metric("IA paga", "BLOQUEADA")

st.warning("Nao automatiza navegador logado. Nao executa sem confirmacao humana. Tudo fica auditado em local_runtime.")

st.subheader("1. Prompt para copiar e colar no K-Atlas Engineer")
prompt = build_engineer_prompt_from_review()
st.code(prompt.get("prompt_text", ""), language="text")

st.subheader("2. Cole aqui a resposta/comando do K-Atlas Engineer")
title = st.text_input("Titulo", value="Comando do K-Atlas Engineer")
response = st.text_area("Resposta ou comando PowerShell", height=260)

if st.button("Stage command local", use_container_width=True):
    st.json(stage_engineer_response(response, title=title))

st.subheader("3. Comandos staged")
for item in list_staged_engineer_commands():
    label = f"{item.get('draft_id')} - safe={item.get('safe_for_confirmed_execution')}"
    with st.expander(label):
        st.write("PS1:", item.get("ps1_path"))
        st.write("Confirmation:", CONFIRMATION_PHRASE)
        st.subheader("Comando confirmado")
        st.code(item.get("confirmed_execution_command", ""), language="powershell")
        st.subheader("Scan")
        st.json(item.get("scan", {}))
