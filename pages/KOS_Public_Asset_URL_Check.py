import streamlit as st
from k_atlas.creative_asset_publisher import inspect_public_asset_url

st.set_page_config(page_title="KOS Public Asset URL Check", layout="wide")

st.title("KOS Public Asset URL Check")
st.caption("Confere se a arte ja possui URL publica HTTPS.")

if st.button("Conferir URL publica", use_container_width=True):
    result = inspect_public_asset_url()
    st.session_state["phase15_url"] = result

result = st.session_state.get("phase15_url") or inspect_public_asset_url()

st.metric("Status", result["status"])
st.metric("URL pronta", result["public_url_ready"])

if result.get("public_url"):
    st.code(result["public_url"])
else:
    st.warning("Ainda sem URL publica. Defina KOS_PUBLIC_BASE_URL ou faca deploy Vercel.")

st.json(result)
