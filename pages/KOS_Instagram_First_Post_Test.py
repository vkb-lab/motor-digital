import streamlit as st
from k_atlas.ig_first_post import build_first_post_package, execute_first_post_if_armed

st.set_page_config(page_title="KOS Instagram First Post Test", layout="wide")

st.title("KOS Instagram First Post Test")
st.caption("Pacote do primeiro teste real controlado. A execucao real exige trava tripla.")

client_id = st.text_input("Cliente", value="parada_atlantida")
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
image_url = st.text_input("URL publica da imagem", value="https://placehold.co/1080x1080/png")
caption = st.text_area("Legenda", value="Primeiro teste controlado preparado pelo K-OS.")

if st.button("Preparar primeiro post", use_container_width=True):
    package = build_first_post_package(client_id, campaign_name, image_url, caption)
    st.session_state["phase12_package"] = package
    st.success("Pacote preparado para revisao.")

package = st.session_state.get("phase12_package")

if package:
    st.subheader("Pacote")
    st.json(package)

    if st.button("Testar trava de execucao", use_container_width=True):
        result = execute_first_post_if_armed(package)
        st.session_state["phase12_result"] = result
        st.warning("Trava testada.")

if "phase12_result" in st.session_state:
    st.subheader("Resultado")
    st.json(st.session_state["phase12_result"])

st.warning("Esta tela nao arma o post real sozinha. A proxima confirmacao sera feita pelo terminal com variaveis locais.")
