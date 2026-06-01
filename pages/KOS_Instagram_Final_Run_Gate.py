import streamlit as st
from k_atlas.ig_final_run import build_phase14_final_package, inspect_phase14_gate

st.set_page_config(page_title="KOS Instagram Final Run Gate", layout="wide")

st.title("KOS Instagram Final Run Gate")
st.caption("Portao final antes do primeiro post real.")

client_id = st.text_input("Cliente", value="parada_atlantida")
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
image_url = st.text_input("URL publica da imagem", value="https://placehold.co/1080x1080/png")
caption = st.text_area("Legenda", value="Primeiro teste controlado preparado pelo K-OS.")

gate = inspect_phase14_gate(load_runtime=True)

st.subheader("Gate")
st.metric("Status", gate["status"])
st.metric("Pronto para envio real", gate["ready_for_real_send"])
st.json(gate)

if st.button("Preparar pacote final", use_container_width=True):
    package = build_phase14_final_package(client_id, campaign_name, image_url, caption, load_runtime=True)
    st.session_state["phase14_package"] = package
    st.success("Pacote final preparado.")

if "phase14_package" in st.session_state:
    st.subheader("Pacote final")
    st.json(st.session_state["phase14_package"])

st.warning("Esta pagina nao publica automaticamente. O envio real exige comando ou controle separado e confirmacao digitada.")
