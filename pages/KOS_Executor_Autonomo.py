import streamlit as st
from k_atlas.command_autopilot import run_autopilot_demo
from k_atlas.autonomous_executor import run_autonomous_command

st.set_page_config(page_title="Executor Autonomo K-OS", layout="wide")

st.title("Executor Autonomo K-OS")
st.caption("Comando unico -> plano -> execucao dry-run -> lousa -> revisao final")

default_command = "Crie uma campanha para Parada Atlantida com landing page, QR Code, post Instagram, criativo visual e fila de publicacao."

command = st.text_area("Comando operacional", value=default_command, height=120)

col1, col2 = st.columns(2)

with col1:
    if st.button("Executar Autopilot Demo", use_container_width=True):
        result = run_autopilot_demo()
        st.session_state["phase6_result"] = result
        st.success("Autopilot executado em dry-run.")

with col2:
    if st.button("Executar comando digitado", use_container_width=True):
        result = run_autonomous_command(command)
        st.session_state["phase6_result"] = result
        st.success("Comando executado em dry-run.")

result = st.session_state.get("phase6_result")

if result:
    st.subheader("Resultado")
    st.metric("Status", result.get("status", ""))
    st.metric("Cliente", result.get("client_id", ""))
    st.metric("Job", result.get("job_id", ""))

    st.subheader("Artefatos")
    st.json(result.get("artifacts", {}).get("items", {}))

    st.subheader("Revisao final")
    st.json(result.get("final_review", {}))

    st.warning("Nenhuma acao real foi executada. Publicacao, DM, anuncio, Google e pagamento continuam bloqueados ate aprovacao manual.")
else:
    st.info("Clique em Executar Autopilot Demo para testar a Fase 6.")
