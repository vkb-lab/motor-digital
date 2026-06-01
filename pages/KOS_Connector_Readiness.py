import streamlit as st
from k_atlas.live_onboarding.readiness_matrix import build_readiness_matrix

st.set_page_config(page_title="KOS Connector Readiness", layout="wide")
st.title("KOS Connector Readiness")
client_id = st.selectbox("Cliente", ["parada_atlantida","casa_da_limpeza","cliente_03","cliente_04","cliente_05"])
st.json(build_readiness_matrix(client_id))
