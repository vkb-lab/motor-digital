import streamlit as st
from k_atlas.public_asset_bridge import build_phase16_public_url_package

st.set_page_config(page_title="KOS Public Image URL Bridge", layout="wide")

st.title("KOS Public Image URL Bridge")
st.caption("Transforma a imagem local em URL publica HTTPS para o Instagram.")

if st.button("Gerar/validar URL publica", use_container_width=True):
    result = build_phase16_public_url_package(attempt_deploy=True)
    st.session_state["phase16_result"] = result

result = st.session_state.get("phase16_result")

if result:
    st.metric("Status", result["status"])
    if result.get("image_url_for_instagram"):
        st.code(result["image_url_for_instagram"])
        st.image(result["image_url_for_instagram"], caption="Imagem publica para Instagram")
    else:
        st.warning("Ainda sem URL publica. Confira Vercel CLI/login ou defina KOS_PUBLIC_BASE_URL.")
    st.json(result)
else:
    st.info("Clique para gerar a URL publica.")
