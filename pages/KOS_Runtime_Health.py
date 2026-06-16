import streamlit as st

from k_atlas.kaizen.runtime_health import build_runtime_health

st.set_page_config(page_title="KOS Runtime Health", layout="wide")

st.title("KOS Runtime Health Monitor")
st.caption("Monitor read-only do K-OS 24/7 local.")

health = build_runtime_health(write_log=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Health", health.get("health_status", "N/A"))
col2.metric("Startup", "SIM" if health.get("startup_folder", {}).get("installed") else "NAO")
col3.metric("Background", "SIM" if health.get("background_processes", {}).get("running") else "NAO")
col4.metric("Git dirty", "SIM" if health.get("git", {}).get("status_short", "").strip() else "NAO")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Scheduler tick", "SIM" if health.get("scheduler_last_tick", {}).get("exists") else "NAO")
col6.metric("IG publish", "BLOQUEADO" if health.get("runtime_locks", {}).get("production_publish_locked") else "ATENCAO")
col7.metric("IA paga", "BLOQUEADA" if health.get("runtime_locks", {}).get("paid_ai_locked") else "ATENCAO")
col8.metric("External actions", "NAO")

if health.get("warnings"):
    st.warning(health.get("warnings"))
else:
    st.success("Runtime saudavel.")

st.subheader("Resumo completo")
st.json(health)

st.subheader("Ultimos commits")
st.code(health.get("git", {}).get("last_commits", ""))

st.warning("Monitor read-only. Nao publica, nao usa IA paga e nao executa Codex automaticamente.")
