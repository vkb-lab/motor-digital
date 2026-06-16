import streamlit as st

from k_atlas.kaizen.windows_task_gate import build_registration_plan, check_windows_task_status

st.set_page_config(page_title="KOS Windows Task Gate", layout="wide")

st.title("KOS Windows Task Registration Gate")
st.caption("Registro 24/7 local exige confirmacao explicita no PowerShell.")

plan = build_registration_plan()
status = check_windows_task_status()

col1, col2, col3 = st.columns(3)
col1.metric("Task", plan["task_name"])
col2.metric("Installed", "SIM" if status.get("installed") else "NAO")
col3.metric("Auto paid/publish", "BLOQUEADO")

st.subheader("Plano")
st.json(plan)

st.subheader("Status da tarefa")
st.json(status)

st.subheader("Comandos manuais")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\register_kos_autonomy_windows_task.ps1")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\unregister_kos_autonomy_windows_task.ps1")

st.warning("Esta pagina nao registra tarefa. O registro so acontece pelo script PowerShell com confirmacao exata.")
