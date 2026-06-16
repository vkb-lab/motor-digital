import streamlit as st

from k_atlas.product_factory.scaffold_writer import (
    get_latest_scaffold_preview,
    build_scaffold_write_plan,
    write_scaffold_from_preview,
    CONFIRMATION_PHRASE,
)

st.set_page_config(page_title="KOS Product Scaffold Writer", layout="wide")

st.title("KOS Product Local Scaffold Writer")
st.caption("Cria scaffold local somente com confirmacao humana explicita.")

preview = get_latest_scaffold_preview()

if not preview:
    st.warning("Nenhum scaffold preview encontrado.")
else:
    plan = build_scaffold_write_plan(preview)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Produto", preview.get("slug", "N/A"))
    col2.metric("Arquivos", len(plan.get("files", [])))
    col3.metric("Diretorios", len(plan.get("directories", [])))
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Plano de escrita")
    st.json(plan)

    st.subheader("Confirmacao exigida")
    st.code(CONFIRMATION_PHRASE)

    confirmation = st.text_input("Confirmacao", "")

    if st.button("Dry-run", use_container_width=True):
        st.json(write_scaffold_from_preview(preview, confirmation=confirmation, dry_run=True))

    if st.button("Criar scaffold local", use_container_width=True):
        result = write_scaffold_from_preview(preview, confirmation=confirmation, dry_run=False)
        st.json(result)

st.warning("Local only. Sem deploy, sem IA paga, sem Instagram, sem segredos.")