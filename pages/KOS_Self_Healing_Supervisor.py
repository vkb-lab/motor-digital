import streamlit as st

from k_atlas.kaizen.self_healing_supervisor import run_self_healing_supervisor

st.set_page_config(page_title="KOS Self-Healing Supervisor", layout="wide")

st.title("KOS Self-Healing Local Supervisor")
st.caption("Diagnostica falhas locais e sugere reparos manuais. Nao executa reparos automaticamente.")

report = run_self_healing_supervisor(write_log=True)
plan = report.get("recovery_plan", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Supervisor", report.get("status", "N/A"))
col2.metric("Issues", len(plan.get("issues", [])))
col3.metric("Commands", len(plan.get("manual_recovery_commands", [])))
col4.metric("Auto repair", "NAO")

if plan.get("issues"):
    st.warning(plan.get("issues"))
else:
    st.success("Nenhum problema critico detectado.")

st.subheader("Comandos manuais sugeridos")
for item in plan.get("manual_recovery_commands", []):
    st.code(item.get("command", ""))
    st.caption(item.get("reason", ""))

st.subheader("Relatorio completo")
st.json(report)

st.warning("Supervisor read-only. Nao publica, nao usa IA paga e nao executa reparo automatico.")
