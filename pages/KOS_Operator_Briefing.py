import streamlit as st

from k_atlas.kaizen.operator_briefing import build_operator_briefing, render_markdown

st.set_page_config(page_title="KOS Operator Briefing", layout="wide")

st.title("KOS Operator Daily Briefing")
st.caption("Resumo operacional read-only para o operador humano.")

briefing = build_operator_briefing(write_log=True)
summary = briefing.get("summary", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Risco", briefing.get("risk_level", "N/A"))
col2.metric("Health", briefing.get("health_status", "N/A"))
col3.metric("Background", "SIM" if summary.get("background_running") else "NAO")
col4.metric("Git dirty", "SIM" if summary.get("git_dirty") else "NAO")

st.subheader("Prioridades")
for item in briefing.get("priorities", []):
    st.write("- " + item)

st.subheader("Comandos seguros")
for item in briefing.get("safe_next_commands", []):
    st.code(item.get("command", ""))

st.subheader("Briefing Markdown")
st.markdown(render_markdown(briefing))

st.warning("Briefing read-only. Nao publica, nao usa IA paga e nao executa reparos.")
