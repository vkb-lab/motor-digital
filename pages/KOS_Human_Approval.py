import streamlit as st

from k_atlas.kaizen.human_approval import (
    create_approval_request,
    approve_dry_run,
    reject_request,
    summarize_approvals,
    DRY_RUN_CONFIRMATION,
)

st.set_page_config(page_title="KOS Human Approval", layout="wide")

st.title("KOS Human Approval Console")
st.caption("Aprovacao humana auditavel. Nesta fase, aprovacao nao executa acao real.")

summary = summarize_approvals()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", summary["total"])
col2.metric("Pending", summary["pending"])
col3.metric("Approved dry-run", summary["approved_dry_run_only"])
col4.metric("Execution allowed", summary["execution_allowed_count"])

st.subheader("Criar pedido de aprovacao")
title = st.text_input("Titulo", value="Aprovar bundle seguro")
description = st.text_area("Descricao", value="Aprovar apenas dry-run. Nenhuma execucao real.")
action_type = st.selectbox("Tipo", ["safe_executor_bundle", "mission_plan", "planner_dry_run"], index=0)
risk_level = st.selectbox("Risco", ["low", "medium", "high"], index=0)

if st.button("Criar pedido", use_container_width=True):
    req = create_approval_request(
        title=title,
        description=description,
        action_type=action_type,
        risk_level=risk_level,
        payload={}
    )
    st.success(f"Pedido criado: {req['id']}")
    st.rerun()

st.subheader("Pedidos")
summary = summarize_approvals()

for req in summary.get("requests", []):
    with st.expander(f"{req.get('id')} - {req.get('title')} - {req.get('status')}"):
        st.json(req)

        typed = st.text_input(
            "Confirmacao obrigatoria",
            key="confirm_" + req.get("id"),
            value=""
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Aprovar dry-run", key="approve_" + req.get("id"), use_container_width=True):
                result = approve_dry_run(req.get("id"), typed)
                st.json(result)
                st.rerun()

        with col_b:
            if st.button("Rejeitar", key="reject_" + req.get("id"), use_container_width=True):
                result = reject_request(req.get("id"), "Rejected from UI")
                st.json(result)
                st.rerun()

st.info(f"Confirmacao para dry-run: {DRY_RUN_CONFIRMATION}")
st.warning("Esta fase nao permite publicacao, IA paga, segredo, Codex automatico ou execucao real.")
