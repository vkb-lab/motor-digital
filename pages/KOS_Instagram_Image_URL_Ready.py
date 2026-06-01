import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="KOS Instagram Image URL Ready", layout="wide")

st.title("KOS Instagram Image URL Ready")
st.caption("Conferencia final da URL da imagem antes do post real.")

path = Path("reports/KOS_PHASE16_PUBLIC_ASSET_URL_PACKAGE.json")

if path.exists():
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    st.metric("Status", data.get("status"))
    url = data.get("image_url_for_instagram", "")
    if url:
        st.code(url)
        st.image(url, caption="Imagem pronta para Instagram")
        st.success("URL publica pronta para o comando final de publicacao.")
    else:
        st.warning("URL ainda nao pronta.")
    st.json(data)
else:
    st.warning("Pacote da Fase 16 ainda nao existe.")
