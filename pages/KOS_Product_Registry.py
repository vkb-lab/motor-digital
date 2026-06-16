import streamlit as st

from k_atlas.product_factory.product_registry import refresh_product_registry, get_latest_registry

st.set_page_config(page_title="KOS Product Registry", layout="wide")

st.title("KOS Product Runtime Registry")
st.caption("Registro auditavel dos produtos locais em products/. Read-only.")

if st.button("Atualizar registry local", use_container_width=True):
    st.json(refresh_product_registry())

latest = get_latest_registry()
snapshot = latest.get("snapshot", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produtos", snapshot.get("products_count", 0))
col2.metric("Seguros", snapshot.get("safe_products_count", 0))
col3.metric("Atenção", snapshot.get("attention_required_count", 0))
col4.metric("Execução", "BLOQUEADA")

st.subheader("Registry")
st.json(latest)

st.warning("Read-only. Nao executa produtos, nao faz deploy, nao usa IA paga, nao publica.")