import streamlit as st

from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission, save_blueprint, summarize_blueprints

st.set_page_config(page_title="KOS Product Blueprint Generator", layout="wide")

st.title("KOS Product Factory Blueprint Generator")
st.caption("Gera blueprint completo a partir de uma missao de produto. Design-only.")

idea = st.text_input("Ideia", "Criar um SaaS de automacao comercial com IA modular")
product_type = st.selectbox("Tipo", ["saas", "app", "landing_page", "campaign", "automation", "api", "agent", "dashboard", "integration"])
target_user = st.text_input("Publico-alvo", "pequenos negocios")
market = st.text_input("Mercado", "automacao comercial")

mission = build_product_mission(
    idea=idea,
    product_type=product_type,
    target_user=target_user,
    market=market,
    priority="medium",
    source="streamlit_blueprint_draft"
)

blueprint = build_blueprint_from_mission(mission)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tipo", blueprint.get("product_type"))
col2.metric("Modulos", len(blueprint.get("architecture", {}).get("modules", [])))
col3.metric("Build", "BLOQUEADO")
col4.metric("Deploy", "BLOQUEADO")

st.subheader("Blueprint")
st.json(blueprint)

if st.button("Salvar blueprint local", use_container_width=True):
    saved = save_blueprint(blueprint)
    st.success("Blueprint salvo no runtime local.")
    st.json(saved)

st.subheader("Resumo")
st.json(summarize_blueprints(limit=20))

st.warning("Design-only. Sem build automatico, sem deploy, sem IA paga, sem Instagram.")
