import streamlit as st

from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot

st.set_page_config(page_title="KOS Autonomy Dashboard", layout="wide")

st.title("KOS Autonomy Dashboard")
st.caption("Cockpit read-only: autonomia, missoes, aprovacoes, executor, Codex/Ollama e travas.")

snapshot = build_autonomy_snapshot(write_log=True)

git = snapshot.get("git", {})
tools = snapshot.get("tools", {})
locks = snapshot.get("runtime_locks", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Branch", git.get("branch", "N/A"))
col2.metric("Git dirty", "SIM" if git.get("status_short", "").strip() else "NAO")
col3.metric("Codex", "OK" if tools.get("codex", {}).get("installed") else "NAO")
col4.metric("Ollama", "OK" if tools.get("ollama", {}).get("installed") else "NAO")

col5, col6, col7, col8 = st.columns(4)
col5.metric("IG producao", "BLOQUEADO" if locks.get("production_publish_locked") else "ATENCAO")
col6.metric("IA paga", "BLOQUEADA" if locks.get("paid_ai_locked") else "ATENCAO")
col7.metric("Parada Atlantida", "LOCKED")
col8.metric("Hupmix", "TEST ONLY")

st.subheader("Mission Queue")
st.json(snapshot.get("mission_queue", {}))

st.subheader("Human Approval")
st.json(snapshot.get("human_approval", {}))

st.subheader("Safe Executor")
st.json(snapshot.get("safe_executor", {}))

st.subheader("Closed Loop")
st.json(snapshot.get("closed_loop", {}))

st.subheader("Runtime redigido")
st.json(snapshot.get("runtime_locks", {}))

st.subheader("Git")
st.code(git.get("status_short", "") or "workspace limpo")
st.code(git.get("last_commits", ""))

st.warning("Dashboard read-only. Nao publica, nao usa IA paga, nao executa Codex automaticamente e nao exibe segredos.")
