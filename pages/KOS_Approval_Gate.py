import streamlit as st
from k_atlas.real_execution_gate import request_real_execution

st.set_page_config(page_title="KOS Approval Gate", layout="wide")
st.title("KOS Approval Gate")
client_id = st.selectbox("Cliente", ["parada_atlantida","casa_da_limpeza","cliente_03","cliente_04","cliente_05"])
platform = st.selectbox("Plataforma", ["instagram","meta_ads","google_business","whatsapp_business","github","vercel","stripe"])
action = st.text_input("Acao", "publish_instagram")
if st.button("Gerar pacote de aprovacao", use_container_width=True):
    st.json(request_real_execution(client_id, platform, action, {"source":"cockpit"}))
