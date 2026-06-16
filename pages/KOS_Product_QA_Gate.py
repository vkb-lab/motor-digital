import streamlit as st

from k_atlas.product_factory.product_qa_gate import (
    refresh_product_qa_gate,
    get_latest_product_qa_report,
)

st.set_page_config(page_title="KOS Product QA Gate", layout="wide")

st.title("KOS Product QA Gate")
st.caption("Avalia qualidade e seguranca dos produtos locais. Read-only.")

if st.button("Atualizar QA Gate", use_container_width=True):
    st.json(refresh_product_qa_gate())

latest = get_latest_product_qa_report()
report = latest.get("report", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produtos", report.get("products_count", 0))
col2.metric("Aprovados", report.get("passed_count", 0))
col3.metric("Atenção", report.get("attention_required_count", 0))
col4.metric("Crítico", report.get("critical_count", 0))

st.subheader("Relatório QA")
st.json(latest)

for item in report.get("qa_items", []):
    title = item.get("title") or item.get("slug") or "Produto"
    with st.expander(f"{title} - {item.get('status')} - score {item.get('score')}"):
        st.write("Path:", item.get("path"))
        st.write("Tipo:", item.get("product_type"))
        st.write("Human review:", item.get("human_review_required"))
        st.json(item)

st.warning("Read-only. Nao executa produto, nao corrige automaticamente, nao deleta, nao faz deploy, nao usa IA paga e nao publica.")