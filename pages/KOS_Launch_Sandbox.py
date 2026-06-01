import streamlit as st
from k_atlas.launch_sandbox import run_launch_sandbox

st.set_page_config(page_title="KOS Launch Sandbox", layout="wide")

st.title("KOS Launch Sandbox")
st.caption("Preparacao de lancamento em sandbox. Nenhuma acao real e executada.")

client_id = st.selectbox("Cliente", ["parada_atlantida", "casa_da_limpeza", "cliente_03", "cliente_04", "cliente_05"])
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
objective = st.text_input("Objetivo", value="lancamento")

if st.button("Gerar sandbox de lancamento", use_container_width=True):
    result = run_launch_sandbox(client_id, campaign_name, objective)
    st.session_state["phase8_launch_result"] = result
    st.success("Sandbox gerado. Abra KOS Launch Confirmation para revisar.")

result = st.session_state.get("phase8_launch_result")
if result:
    st.subheader("Resultado")
    st.metric("Status", result["status"])
    st.metric("Cliente", result["client_id"])
    st.json(result)
else:
    st.info("Clique no botao para gerar o sandbox.")
