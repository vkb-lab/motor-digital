import streamlit as st

from k_atlas.kaizen.startup_folder_gate import build_startup_plan, check_startup_status

st.set_page_config(page_title="KOS Startup Folder Gate", layout="wide")

st.title("KOS Startup Folder Gate")
st.caption("Fallback sem admin para iniciar K-OS no login do usuario.")

plan = build_startup_plan()
status = check_startup_status()

col1, col2, col3 = st.columns(3)
col1.metric("Entry", plan["entry_name"])
col2.metric("Installed", "SIM" if status.get("installed") else "NAO")
col3.metric("Requires admin", "NAO")

st.subheader("Plano")
st.json(plan)

st.subheader("Status")
st.json(status)

st.subheader("Comandos")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\register_kos_autonomy_startup_folder.ps1")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\unregister_kos_autonomy_startup_folder.ps1")

st.warning("Esta pagina nao registra nada. O registro exige PowerShell e confirmacao exata.")
