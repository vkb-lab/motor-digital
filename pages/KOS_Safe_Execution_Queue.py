import streamlit as st
from k_atlas.safe_execution.channel_queue import build_channel_queue

st.set_page_config(page_title="KOS Safe Execution Queue", layout="wide")

st.title("KOS Safe Execution Queue")
st.caption("Fila de execucao por canal. Nenhuma acao real.")

client_id = st.selectbox("Cliente", ["parada_atlantida", "casa_da_limpeza", "cliente_03", "cliente_04", "cliente_05"])
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")

queue = build_channel_queue(client_id, campaign_name)

st.metric("Status", queue["status"])
for item in queue["items"]:
    with st.container(border=True):
        st.write(f"**{item['channel']}**")
        st.write(f"Status: `{item['status']}`")
        st.write(f"Modo: `{item['mode']}`")
        st.write(f"Acao real executada: `{item['real_action_executed']}`")
