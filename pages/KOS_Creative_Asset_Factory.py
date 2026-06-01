import streamlit as st
from k_atlas.creative_asset_publisher import build_campaign_asset

st.set_page_config(page_title="KOS Creative Asset Factory", layout="wide")

st.title("KOS Creative Asset Factory")
st.caption("Gerador local de arte PNG para campanhas.")

client_id = st.text_input("Cliente", value="parada_atlantida")
campaign_name = st.text_input("Campanha", value="campanha_lancamento_parada_atlantida")
title = st.text_input("Titulo", value="PARADA ATLANTIDA")
subtitle = st.text_input("Subtitulo", value="LANCAMENTO DIGITAL")
cta = st.text_input("CTA", value="CONFIRA AS NOVIDADES")

if st.button("Gerar arte PNG", use_container_width=True):
    asset = build_campaign_asset(client_id, campaign_name, title, subtitle, cta)
    st.session_state["phase15_asset"] = asset
    st.success("Arte criada em public/kos/assets.")

asset = st.session_state.get("phase15_asset")
if asset:
    st.json(asset)
    st.image(asset["local_png_path"], caption="Arte gerada pelo K-OS")
else:
    st.info("Clique para gerar a arte da campanha.")
