import streamlit as st

from k_atlas.product_factory.product_cockpit_launcher import (
    refresh_product_cockpit_launcher,
    get_latest_launcher_snapshot,
)

st.set_page_config(page_title="KOS Product Cockpit Launcher", layout="wide")

st.title("KOS Product Cockpit Launcher")
st.caption("Lista produtos e mostra instrucoes locais. Nao executa comandos.")

if st.button("Atualizar launcher", use_container_width=True):
    st.json(refresh_product_cockpit_launcher())

latest = get_latest_launcher_snapshot()
snapshot = latest.get("snapshot", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produtos", snapshot.get("products_count", 0))
col2.metric("Seguros", snapshot.get("safe_products_count", 0))
col3.metric("Atenção", snapshot.get("attention_required_count", 0))
col4.metric("Execução", "BLOQUEADA")

st.subheader("Launcher Snapshot")
st.json(latest)

for item in snapshot.get("launch_items", []):
    with st.expander(item.get("title") or item.get("slug") or "Produto"):
        st.write("Tipo:", item.get("product_type"))
        st.write("Path:", item.get("path"))
        st.write("Seguro:", item.get("safe"))
        st.subheader("Comandos manuais")
        for command in item.get("commands", []):
            st.code(command.get("command", ""))
            st.caption("execution_allowed_now: False")

st.warning("Read-only. Nao executa produto, nao roda shell, nao faz deploy, nao usa IA paga, nao publica.")