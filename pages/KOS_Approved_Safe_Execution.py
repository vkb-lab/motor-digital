import streamlit as st
from k_atlas.safe_execution import run_approved_safe_execution

st.set_page_config(page_title="KOS Approved Safe Execution", layout="wide")

st.title("KOS Approved Safe Execution")
st.caption("Executa a aprovacao humana em modo sandbox por canal.")

client_id = st.selectbox("Cliente", ["parada_atlantida", "casa_da_limpeza", "cliente_03", "cliente_04", "cliente_05"])
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
decision = st.selectbox("Decisao humana", ["OK", "AJUSTAR", "BLOQUEAR"])

if st.button("Executar aprovacao segura", use_container_width=True):
    result = run_approved_safe_execution(client_id, campaign_name, decision)
    st.session_state["phase9_result"] = result
    st.success("Execucao segura preparada.")

result = st.session_state.get("phase9_result")
if result:
    st.metric("Status", result.get("status"))
    st.metric("Cliente", result.get("client_id"))
    st.json(result)
else:
    st.info("Clique para executar a aprovacao segura.")
