import streamlit as st

from k_atlas.kaizen.local_patch_workspace import (
    create_work_orders_from_coworker_tasks,
    get_latest_patch_workspace_status,
    load_existing_work_orders,
)

st.set_page_config(page_title="KOS Local Patch Workspace", layout="wide")

st.title("K-OS Local Patch Workspace")
st.caption("Transforma tarefas do coworker em work orders locais. Nao altera o repositorio.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "LOCAL")
col2.metric("Autonomia", "TIER 2")
col3.metric("Repo write", "BLOQUEADO")
col4.metric("Patch apply", "BLOQUEADO")

st.warning("Este workspace prepara planos. Ele nao aplica patches, nao altera arquivos do repo, nao faz commit, nao faz push, nao usa IA paga e nao publica.")

if st.button("Criar work orders agora", use_container_width=True):
    st.json(create_work_orders_from_coworker_tasks(limit=10))

latest = get_latest_patch_workspace_status()
orders = load_existing_work_orders(limit=20)

st.subheader("Status")
st.json(latest)

st.subheader("Work orders")
if not orders:
    st.info("Nenhuma work order local ainda.")
else:
    for order in orders:
        label = f"{order.get('work_order_id')} - {order.get('title')} - risco {order.get('risk')}"
        with st.expander(label):
            st.write("Task type:", order.get("task_type"))
            st.write("Source task:", order.get("source_task_id"))
            st.write("Next step:", order.get("next_step"))
            st.subheader("Arquivos propostos")
            st.json(order.get("proposed_repo_files", []))
            st.subheader("Comando preview")
            st.code(order.get("operator_command_preview", ""), language="powershell")
            st.subheader("Gates")
            st.json(order.get("gates", {}))