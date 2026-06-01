import streamlit as st
from k_atlas.ig_final_run import build_phase14_final_package, execute_phase14_if_confirmed
from k_atlas.ig_final_run.final_runner import FINAL_TYPED_CONFIRMATION

st.set_page_config(page_title="KOS Instagram Real Send Control", layout="wide")

st.title("KOS Instagram Real Send Control")
st.caption("Controle manual do primeiro envio real. Use somente depois da revisao final.")

client_id = st.text_input("Cliente", value="parada_atlantida")
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
image_url = st.text_input("URL publica da imagem", value="https://placehold.co/1080x1080/png")
caption = st.text_area("Legenda", value="Primeiro teste controlado preparado pelo K-OS.")

typed = st.text_input("Digite a confirmacao final", value="")
execute_switch = st.checkbox("Confirmo tentativa real controlada")

st.code(f"Confirmacao exigida: {FINAL_TYPED_CONFIRMATION}")

if st.button("Executar gate final", use_container_width=True):
    package = build_phase14_final_package(client_id, campaign_name, image_url, caption, load_runtime=True)
    result = execute_phase14_if_confirmed(
        package,
        typed_confirmation=typed,
        execute_real_confirmed=execute_switch,
    )
    st.session_state["phase14_result"] = result

if "phase14_result" in st.session_state:
    st.subheader("Resultado")
    st.json(st.session_state["phase14_result"])

st.error("Atencao: com todas as travas ativas, este controle pode publicar real.")
