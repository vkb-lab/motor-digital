import streamlit as st

from k_atlas.kaizen.scheduler_gate import summarize_scheduler, run_scheduler_tick

st.set_page_config(page_title="KOS Scheduler Gate", layout="wide")

st.title("KOS Autonomy Scheduler Manual Gate")
st.caption("Preparacao para recorrencia local. Nao registra tarefa Windows e nao liga 24/7 automaticamente.")

summary = summarize_scheduler()
plan = summary.get("plan", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Mode", plan.get("mode", "N/A"))
col2.metric("Windows task", "ON" if plan.get("windows_task_registered") else "OFF")
col3.metric("Auto start", "ON" if plan.get("auto_start_enabled") else "OFF")
col4.metric("Interval", plan.get("default_interval_seconds", 900))

st.subheader("Plano de scheduler")
st.json(plan)

st.subheader("Rodar um tick manual seguro")
if st.button("Rodar tick manual", use_container_width=True):
    result = run_scheduler_tick("streamlit_manual_tick")
    st.json(result)

st.subheader("Ultimo tick")
st.json(summary.get("last_tick", {}))

st.warning("Esta fase nao registra agendamento automatico. A Fase 43 exige confirmacao explicita.")
