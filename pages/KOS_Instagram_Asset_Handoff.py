import streamlit as st
from k_atlas.creative_asset_publisher import build_instagram_asset_handoff

st.set_page_config(page_title="KOS Instagram Asset Handoff", layout="wide")

st.title("KOS Instagram Asset Handoff")
st.caption("Entrega a arte final e a URL para o publicador do Instagram.")

client_id = st.text_input("Cliente", value="parada_atlantida")
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
title = st.text_input("Titulo", value="PARADA ATLANTIDA")
subtitle = st.text_input("Subtitulo", value="LANCAMENTO DIGITAL")
cta = st.text_input("CTA", value="CONFIRA AS NOVIDADES")
caption = st.text_area("Legenda", value="Primeiro teste controlado da campanha Parada Atlantida.")

if st.button("Criar handoff Instagram", use_container_width=True):
    result = build_instagram_asset_handoff(client_id, campaign_name, title, subtitle, cta, caption)
    st.session_state["phase15_handoff"] = result
    st.success("Handoff gerado.")

result = st.session_state.get("phase15_handoff")

if result:
    st.metric("Status", result["status"])
    if result.get("image_url_for_instagram"):
        st.code(result["image_url_for_instagram"])
    else:
        st.warning("Handoff criado, mas falta URL publica HTTPS.")
    st.image(result["asset"]["local_png_path"], caption="Arte final")
    st.json(result)
else:
    st.info("Clique para gerar o pacote de imagem para Instagram.")
