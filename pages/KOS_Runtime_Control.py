import streamlit as st

from k_atlas.kaizen.runtime_control import build_runtime_control_status

st.set_page_config(page_title="KOS Runtime Control", layout="wide")

st.title("KOS Runtime Control")
st.caption("Painel read-only com comandos manuais seguros para controle local.")

status = build_runtime_control_status()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Startup", "SIM" if status.get("startup_installed") else "NAO")
col2.metric("Background", "SIM" if status.get("background_running") else "NAO")
col3.metric("Health", status.get("health_status", "N/A"))
col4.metric("Git dirty", "SIM" if status.get("git_dirty") else "NAO")

col5, col6 = st.columns(2)
col5.metric("IG producao", "BLOQUEADO" if status.get("production_publish_locked") else "ATENCAO")
col6.metric("IA paga", "BLOQUEADA" if status.get("paid_ai_locked") else "ATENCAO")

st.subheader("Comandos seguros")
for item in status.get("safe_commands", []):
    st.code(item.get("command", ""))

st.subheader("Status completo")
st.json(status)

st.warning("Esta pagina nao inicia nem para processos. Use os comandos PowerShell com confirmacao humana.")
