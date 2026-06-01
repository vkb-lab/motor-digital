import streamlit as st
from k_atlas.ig_real_gate.publisher_gate import build_ig_publish_package, execute_ig_real_publish

st.set_page_config(page_title="KOS Instagram Real Publisher Gate", layout="wide")

st.title("KOS Instagram Real Publisher Gate")
st.caption("Primeira ponte real do Instagram com trava final.")

client_id = st.text_input("Cliente", value="parada_atlantida")
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
image_url = st.text_input("URL publica da imagem", value="https://placehold.co/1080x1080/png")
caption = st.text_area("Legenda", value="Preview de campanha preparado pelo K-OS.")

if st.button("Preparar pacote Instagram", use_container_width=True):
    package = build_ig_publish_package(client_id, campaign_name, image_url, caption)
    st.session_state["phase11_package"] = package
    st.success("Pacote preparado.")

package = st.session_state.get("phase11_package")

if package:
    st.subheader("Pacote")
    st.json(package)

    if st.button("Testar gate real", use_container_width=True):
        result = execute_ig_real_publish(package)
        st.session_state["phase11_result"] = result
        st.warning("Gate testado. Se nao houver flags reais, deve ficar bloqueado.")

if "phase11_result" in st.session_state:
    st.subheader("Resultado")
    st.json(st.session_state["phase11_result"])

st.warning("Publicacao real so ocorre com ambiente completo e OK humano final.")
