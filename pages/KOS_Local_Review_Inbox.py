import streamlit as st

from k_atlas.kaizen.local_review_inbox import collect_review_inbox, get_latest_review_inbox

st.set_page_config(page_title="KOS Local Review Inbox", layout="wide")

st.title("K-OS Local Review Inbox")
st.caption("Centraliza comandos, tasks, work orders, drafts e status do loop local.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "LOCAL")
col2.metric("Review", "ATIVO")
col3.metric("Execucao", "BLOQUEADA")
col4.metric("Repo write", "BLOQUEADO")

st.warning("Review-only. Esta tela nao executa comandos, nao altera repo, nao faz commit, nao faz push, nao usa IA paga e nao publica.")

if st.button("Atualizar Review Inbox", use_container_width=True):
    st.json(collect_review_inbox(limit=20))

data = get_latest_review_inbox()
summary = data.get("summary", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Comandos", summary.get("commands_count", 0))
c2.metric("Tasks", summary.get("tasks_count", 0))
c3.metric("Work Orders", summary.get("work_orders_count", 0))
c4.metric("Drafts", summary.get("command_drafts_count", 0))

st.subheader("Bundle para enviar ao K-Atlas Engineer")
bundle = data.get("review_bundle", {})
st.code(bundle.get("bundle_text", ""), language="text")

st.subheader("Command Draft mais recente")
latest_draft = bundle.get("latest_command_draft", {})
st.code(latest_draft.get("powershell_command", "Nenhum draft disponivel."), language="powershell")

with st.expander("Comandos recebidos"):
    st.json(data.get("commands", []))

with st.expander("Tasks"):
    st.json(data.get("tasks", []))

with st.expander("Work Orders"):
    st.json(data.get("work_orders", []))

with st.expander("Command Drafts"):
    st.json(data.get("command_drafts", []))

with st.expander("Loop Status"):
    st.json(data.get("loop_status", {}))