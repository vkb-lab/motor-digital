import streamlit as st

from k_atlas.kaizen.briefing_scheduler import run_briefing_scheduler_tick, summarize_briefing_scheduler

st.set_page_config(page_title="KOS Briefing Scheduler", layout="wide")

st.title("KOS Briefing Scheduler")
st.caption("Integra scheduler local com briefing operacional read-only.")

summary = summarize_briefing_scheduler()
last_tick = summary.get("last_tick", {})

col1, col2, col3 = st.columns(3)
col1.metric("Last tick exists", "SIM" if summary.get("last_tick_exists") else "NAO")
col2.metric("Tick status", last_tick.get("status", "N/A"))
col3.metric("External actions", "NAO")

if st.button("Rodar tick com briefing agora", use_container_width=True):
    result = run_briefing_scheduler_tick("streamlit_phase47_tick")
    st.json(result)

st.subheader("Resumo")
st.json(summary)

st.warning("Read-only. Nao publica, nao usa IA paga, nao executa Codex e nao commita automaticamente.")
