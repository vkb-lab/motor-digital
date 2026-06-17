import streamlit as st

from k_atlas.kaizen.work_order_route_registry import (
    get_work_order_route_registry_status,
    route_work_order_task,
)

st.set_page_config(page_title="KOS Work Order Route Registry", layout="wide")

st.title("K-OS Work Order Route Registry")
st.caption("Roteamento de work orders por JSON versionado.")

status = get_work_order_route_registry_status()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Status", status.get("status"))
c2.metric("Rotas", status.get("routes_count", 0))
c3.metric("Execucao", "BLOQUEADA")
c4.metric("Deploy", "BLOQUEADO")

st.warning("Esta tela e read-only. Nao executa comandos, nao faz deploy, nao usa IA paga e nao publica.")

st.subheader("Registry")
st.json(status)

st.subheader("Teste rapido de roteamento")
title = st.text_input("Titulo", value="Fase 64 - Product Export ZIP Writer Gate")
body = st.text_area("Body", value="Criar Fase 64 usando Product Export Packager da Fase 63 e confirmar YES_CREATE_PRODUCT_EXPORT_ZIP_LOCAL_ONLY.")

if st.button("Testar rota", use_container_width=True):
    task = {
        "title": title,
        "body": body,
        "classification": {
            "task_type": "general_operation",
        },
    }
    st.json(route_work_order_task(task))
