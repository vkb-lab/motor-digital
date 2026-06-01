import streamlit as st
from k_atlas.live_onboarding import generate_client_onboarding

st.set_page_config(page_title="KOS Live Onboarding", layout="wide")
st.title("KOS Live Onboarding")
client_id = st.selectbox("Cliente", ["parada_atlantida","casa_da_limpeza","cliente_03","cliente_04","cliente_05"])
if st.button("Gerar onboarding do cliente", use_container_width=True):
    st.json(generate_client_onboarding(client_id))
st.warning("Nao inserir tokens no cockpit. Use env local ou local_secrets fora do Git.")
