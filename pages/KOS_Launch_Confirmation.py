import json
from pathlib import Path
import streamlit as st

from k_atlas.launch_sandbox import run_launch_sandbox

st.set_page_config(page_title="KOS Launch Confirmation", layout="wide")

st.title("KOS Launch Confirmation")
st.caption("Tela de confirmacao humana antes da proxima etapa.")

ROOT = Path.cwd()
confirmation_path = ROOT / "reports" / "KOS_PHASE8_CONFIRMATION_DEMO.json"

if st.button("Gerar confirmacao demo", use_container_width=True):
    result = run_launch_sandbox()
    st.session_state["phase8_confirmation"] = result["confirmation"]
    st.success("Confirmacao preparada.")

if "phase8_confirmation" in st.session_state:
    data = st.session_state["phase8_confirmation"]
elif confirmation_path.exists():
    data = json.loads(confirmation_path.read_text(encoding="utf-8-sig"))
else:
    data = None

if data:
    st.metric("Status", data.get("status"))
    st.metric("Cliente", data.get("client_id"))
    st.metric("Campanha", data.get("campaign_name"))
    st.subheader("Resumo")
    st.write(data.get("summary"))
    st.subheader("Pacote")
    st.json(data)
    st.warning("Aguardando OK humano. Nenhuma publicacao real foi executada.")
else:
    st.info("Nenhuma confirmacao encontrada. Clique em Gerar confirmacao demo.")
