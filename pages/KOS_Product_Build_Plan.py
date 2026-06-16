import streamlit as st

from k_atlas.product_factory.blueprint_generator import get_latest_product_mission, build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint, save_build_plan, summarize_build_plans

st.set_page_config(page_title="KOS Product Build Plan", layout="wide")

st.title("KOS Product Factory Build Plan")
st.caption("Transforma blueprint em plano tecnico de construcao. Dry-run only.")

mission = get_latest_product_mission()

if not mission:
    st.warning("Nenhuma missao local encontrada ainda.")
else:
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", plan.get("product_type"))
    col2.metric("Arquivos sugeridos", len(plan.get("suggested_files", [])))
    col3.metric("Build", "BLOQUEADO")
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Build Plan")
    st.json(plan)

    if st.button("Salvar build plan local", use_container_width=True):
        saved = save_build_plan(plan)
        st.success("Build plan salvo no runtime local.")
        st.json(saved)

st.subheader("Resumo")
st.json(summarize_build_plans(limit=20))

st.warning("Dry-run only. Nao cria produto real, nao executa build, nao usa IA paga, nao publica.")
