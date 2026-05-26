import streamlit as st
import os
import subprocess
from agent_core import MotorDigitalCore
from self_evolution import SelfEvolution
from marketing_manager import MarketingManager
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Central de Comando — Motor Digital", layout="wide", page_icon="🤖")

# Inicialização do Agente
if 'agent' not in st.session_state:
    st.session_state.agent = MotorDigitalCore()
    st.session_state.evo = SelfEvolution(st.session_state.agent)
    st.session_state.mkt = MarketingManager(st.session_state.agent)
    st.session_state.logs = []

def add_log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

# Interface Lateral (Status)
with st.sidebar:
    st.title("⚙️ Status do Core")
    st.success("Agente Online")
    st.info(f"OS: {st.session_state.agent.os_type}")
    st.write(f"📂 Workspace: `{st.session_state.agent.workspace}`")
    
    if st.button("🔄 Reiniciar Cérebro"):
        st.rerun()
    
    st.markdown("---")
    st.subheader("🔍 Diagnóstico de IA")
    if st.button("Listar Modelos Permitidos"):
        models = st.session_state.agent.get_available_models()
        for m in models:
            st.code(m)

# Área Principal
st.title("🤖 Central de Comando do Agente Autônomo")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Ordens ao Agente")
    order = st.text_input("O que o agente deve fazer no seu Windows agora?", placeholder="Ex: Crie um projeto para a Parada Atlântida")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚀 Executar Ordem"):
            if order:
                add_log(f"Ordem recebida: {order}")
                # Aqui o Gemini processa a ordem e decide qual função do core chamar
                prompt = f"O usuário deu a seguinte ordem ao agente local: '{order}'. O que devo fazer? Responda com a ação a ser tomada."
                resposta = st.session_state.agent.call_gemini(order, system_instruction="Você é o cérebro de um agente autônomo local. Decida a melhor ação.")
                st.write(f"**Pensamento do Agente:** {resposta}")
                add_log("Ação processada pela IA.")
    
    with c2:
        if st.button("🧬 Autoevolução"):
            add_log("Iniciando ciclo de autoevolução...")
            if st.session_state.evo.analyze_self('agent_core.py'):
                st.success("O Agente evoluiu seu próprio código com sucesso!")
                add_log("Autoevolução concluída.")
    
    with c3:
        if st.button("📁 Abrir Workspace"):
            subprocess.run(f"explorer {st.session_state.agent.workspace}", shell=True)
            add_log("Pasta Workspace aberta no Windows Explorer.")
        if st.button("🪟 Ver Janelas"):
            wins = st.session_state.agent.list_open_windows()
            st.write("**Janelas Abertas:**")
            for w in wins:
                st.text(f"• {w}")
            add_log("Janelas do sistema listadas.")
    
    st.markdown("---")
    st.subheader("🎨 Ferramentas de Marketing")
    cm1, cm2 = st.columns(2)
    with cm1:
        if st.button("✨ Abrir Canva & IAs"):
            msg = st.session_state.mkt.open_creative_tools()
            add_log(msg)
    with cm2:
        if st.button("📊 Plano de Recuperação"):
            with st.spinner("Gerando plano estratégico..."):
                plano = st.session_state.mkt.generate_marketing_plan()
                st.info(plano)
                add_log("Plano de marketing gerado.")
    
    st.markdown("---")
    st.subheader("🦅 Visão Águia (Automação Real)")
    if st.button("🚀 Iniciar Navegador IA (Auto-Login)"):
        add_log("Iniciando Chrome com perfil de usuário...")
        st.session_state.agent.start_automated_browser("https://www.instagram.com")
        st.success("Navegador Automatizado aberto no Instagram.")
    
    if st.button("📧 Ler Gmail & Gerar Relatório"):
        add_log("Acessando Gmail para triagem...")
        with st.spinner("Lendo e-mails..."):
            relatorio = st.session_state.agent.call_gemini("Verifique meu gmail e faça um relatório.", system_instruction="Ação: [ACTION:READ_GMAIL]")
            st.write(relatorio)
            add_log("Relatório de e-mails concluído.")

    st.markdown("---")
    st.subheader("📑 Arquivos no Workspace")
    files = os.listdir(st.session_state.agent.workspace)
    if files:
        for f in files:
            st.text(f"📄 {f}")
    else:
        st.write("Workspace vazio.")

with col2:
    st.subheader("📜 Logs do Sistema")
    log_box = st.empty()
    log_content = "\n".join(st.session_state.logs[::-1])
    st.text_area("Atividade em tempo real:", value=log_content, height=400)

# Rodapé
st.markdown("---")
st.caption("Motor Digital Core v2.1 — Engenharia Autônoma Local")
