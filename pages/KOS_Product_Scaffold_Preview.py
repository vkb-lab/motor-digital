import streamlit as st

from k_atlas.product_factory.scaffold_preview import (
    get_latest_build_plan,
    build_scaffold_preview_from_build_plan,
    save_scaffold_preview,
    summarize_scaffold_previews,
)

st.set_page_config(page_title="KOS Product Scaffold Preview", layout="wide")

st.title("KOS Product Factory Scaffold Preview")
st.caption("Gera preview de scaffold a partir do build plan. Dry-run only.")

build_plan = get_latest_build_plan()

if not build_plan:
    st.warning("Nenhum build plan local encontrado ainda.")
else:
    preview = build_scaffold_preview_from_build_plan(build_plan)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", preview.get("product_type"))
    col2.metric("Arquivos", len(preview.get("files_preview", [])))
    col3.metric("Criar arquivos", "BLOQUEADO")
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Scaffold Preview")
    st.json(preview)

    if st.button("Salvar preview local", use_container_width=True):
        saved = save_scaffold_preview(preview)
        st.success("Scaffold preview salvo no runtime local.")
        st.json(saved)

st.subheader("Resumo")
st.json(summarize_scaffold_previews(limit=20))

st.warning("Dry-run only. Nao cria arquivos reais de produto, nao executa build, nao usa IA paga, nao publica.")
