import streamlit as st

from k_atlas.product_factory.product_export_zip_writer_gate import (
    refresh_product_export_zip_writer_gate,
    get_latest_product_export_zip_writer_report,
    CONFIRMATION_PHRASE,
)

st.set_page_config(page_title="KOS Product Export ZIP Writer Gate", layout="wide")

st.title("K-OS Product Export ZIP Writer Gate")
st.caption("Gate humano para criar zip exportavel local. Bloqueado por padrao.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "GATED")
col2.metric("Zip default", "BLOQUEADO")
col3.metric("Deploy", "BLOQUEADO")
col4.metric("Publicacao", "BLOQUEADA")

st.warning("Esta tela valida pacotes. Zip so deve ser criado por script confirmado e com frase humana explicita.")

if st.button("Atualizar ZIP Writer Gate", use_container_width=True):
    st.json(refresh_product_export_zip_writer_gate())

latest = get_latest_product_export_zip_writer_report()
report = latest.get("report", latest)

c1, c2, c3 = st.columns(3)
c1.metric("Produtos", report.get("products_count", 0))
c2.metric("Prontos para zip", report.get("ready_for_zip_count", 0))
c3.metric("Bloqueados", report.get("blocked_count", 0))

st.subheader("Confirmacao exigida")
st.code(CONFIRMATION_PHRASE, language="text")

st.subheader("Relatorio")
st.json(latest)

for item in report.get("validations", []):
    label = f"{item.get('title') or item.get('slug')} - {item.get('status')}"
    with st.expander(label):
        st.write("Files to zip:", item.get("files_to_zip_count"))
        st.subheader("Arquivos validados")
        st.json(item.get("files_to_zip", []))
        st.subheader("Erros")
        st.json(item.get("validation_errors", []))
        st.subheader("Comando confirmado manual futuro")
        st.code(
            f'powershell -ExecutionPolicy Bypass -File scripts\\run_phase64_product_export_zip_writer_confirmed.ps1 -ProductSlug "{item.get("slug")}" -Confirmation "{CONFIRMATION_PHRASE}"',
            language="powershell"
        )
        st.subheader("Gates")
        st.json(item.get("gates", {}))