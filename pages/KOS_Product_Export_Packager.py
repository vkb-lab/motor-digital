import streamlit as st

from k_atlas.product_factory.product_export_packager import (
    refresh_product_export_packager,
    get_latest_product_export_packager_report,
)

st.set_page_config(page_title="KOS Product Export Packager", layout="wide")

st.title("K-OS Product Export Packager")
st.caption("Prepara manifestos exportaveis. Nao cria zip, nao copia arquivos e nao faz deploy.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "READ ONLY")
col2.metric("Zip", "BLOQUEADO")
col3.metric("Deploy", "BLOQUEADO")
col4.metric("Publicacao", "BLOQUEADA")

st.warning("Esta tela apenas gera manifestos e planos. Ela nao cria zip, nao copia arquivos, nao executa shell, nao faz deploy, nao usa IA paga e nao publica.")

if st.button("Atualizar Export Packager", use_container_width=True):
    st.json(refresh_product_export_packager())

latest = get_latest_product_export_packager_report()
report = latest.get("report", {})

c1, c2, c3 = st.columns(3)
c1.metric("Produtos", report.get("products_count", 0))
c2.metric("Prontos", report.get("ready_count", 0))
c3.metric("Atenção", report.get("attention_required_count", 0))

st.subheader("Relatorio")
st.json(latest)

for manifest in report.get("manifests", []):
    label = f"{manifest.get('title') or manifest.get('slug')} - {manifest.get('status')}"
    with st.expander(label):
        st.write("Path:", manifest.get("path"))
        st.write("Safe:", manifest.get("safe"))
        st.write("Allowed files:", manifest.get("allowed_files_count"))
        st.write("Blocked files:", manifest.get("blocked_files_count"))

        st.subheader("Allowed files")
        st.json(manifest.get("allowed_files", []))

        st.subheader("Blocked files")
        st.json(manifest.get("blocked_files", []))

        st.subheader("Future zip plan")
        st.json(manifest.get("future_zip_plan", {}))

        st.subheader("Gates")
        st.json(manifest.get("gates", {}))