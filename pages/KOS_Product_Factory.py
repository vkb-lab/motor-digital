import streamlit as st

from k_atlas.product_factory.mission_layer import (
    build_product_mission,
    append_product_mission,
    summarize_product_missions,
    export_to_kaizen_mission_dry_run,
)

st.set_page_config(page_title="KOS Product Factory", layout="wide")

st.title("KOS Product Factory Mission Layer")
st.caption("Transforma ideias em missoes estruturadas. Nao executa build, deploy ou publicacao.")

idea = st.text_input("Ideia", "Criar um SaaS simples de automacao comercial com IA")
product_type = st.selectbox(
    "Tipo",
    ["saas", "app", "landing_page", "campaign", "automation", "api", "agent", "dashboard", "integration"]
)
target_user = st.text_input("Publico-alvo", "pequenos negocios")
market = st.text_input("Mercado", "automacao e marketing")
priority = st.selectbox("Prioridade", ["low", "medium", "high"], index=1)

draft = build_product_mission(
    idea=idea,
    product_type=product_type,
    target_user=target_user,
    market=market,
    priority=priority,
    source="streamlit_draft"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tipo", draft.get("product_type"))
col2.metric("Tasks", len(draft.get("tasks", [])))
col3.metric("Execution", "BLOQUEADA")
col4.metric("Risk", draft.get("risk_level"))

st.subheader("Missao draft")
st.json(draft)

st.subheader("Export dry-run")
st.json(export_to_kaizen_mission_dry_run(draft))

if st.button("Salvar missao local", use_container_width=True):
    saved = append_product_mission(draft)
    st.success("Missao salva no runtime local.")
    st.json(saved)

st.subheader("Resumo")
st.json(summarize_product_missions(limit=20))

st.warning("Design-only. Sem IA paga, sem Instagram, sem Codex automatico, sem deploy.")
