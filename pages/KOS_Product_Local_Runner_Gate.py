import streamlit as st

from k_atlas.product_factory.product_local_runner_gate import (
    refresh_product_local_runner_gate,
    get_latest_product_local_runner_gate_report,
)

st.set_page_config(page_title="KOS Product Local Runner Gate", layout="wide")

st.title("K-OS Product Local Runner Gate")
st.caption("Prepara comandos manuais de execucao local. Nao executa produtos.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Modo", "READ ONLY")
col2.metric("Execucao", "MANUAL")
col3.metric("Shell", "BLOQUEADO")
col4.metric("Deploy", "BLOQUEADO")

st.warning("Esta tela apenas mostra comandos manuais. Ela nao executa produto, nao roda shell, nao faz deploy, nao usa IA paga e nao publica.")

if st.button("Atualizar Runner Gate", use_container_width=True):
    st.json(refresh_product_local_runner_gate())

latest = get_latest_product_local_runner_gate_report()
report = latest.get("report", {})

c1, c2, c3 = st.columns(3)
c1.metric("Produtos", report.get("products_count", 0))
c2.metric("Prontos", report.get("ready_count", 0))
c3.metric("Atenção", report.get("attention_required_count", 0))

st.subheader("Relatorio")
st.json(latest)

for item in report.get("items", []):
    label = f"{item.get('title') or item.get('slug')} - {item.get('status')}"
    with st.expander(label):
        st.write("Path:", item.get("path"))
        st.write("app.py:", item.get("has_app_py"))
        st.write("tests:", item.get("has_tests_dir"))
        st.write("safe:", item.get("safe"))
        st.subheader("Comandos manuais sugeridos")
        for command in item.get("manual_commands", []):
            st.code(command.get("command", ""), language="powershell")
            st.caption("execution_allowed_now: False")
        st.subheader("Gates")
        st.json(item.get("gates", {}))