import streamlit as st
import pandas as pd

# Configuração da Página para Celular
st.set_page_config(page_title="Torre de Controle IA", layout="centered", initial_sidebar_state="collapsed")

st.title("🛸 MDE - Motor Digital")
st.caption("Sistema Autoevolutivo de Gestão por IA")

# Abas de Navegação Dinâmicas
tab_home, tab_negocios, tab_portal, tab_workspace = st.tabs(["🏠 Home", "💼 Lojas", "🌐 Portal Atlântida", "📥 Workspace"])

with tab_home:
    st.subheader("⚡ Status do Sistema")
    st.success("IA Operando em Modo Autônomo")
    st.metric(label="Leads Captados Hoje", value="142", delta="+22%")
    
    # Campo de Autoevolução (Onde você manda a IA alterar o app)
    st.markdown("---")
    st.subheader("🛠️ Autoevolução da Interface")
    prompt_evolucao = st.text_input("O que você deseja alterar ou criar neste app?")
    if st.button("Executar Mutação de Código"):
        st.info("Gemini processando alteração de layout...")

with tab_negocios:
    st.subheader("🏪 Gerenciador Multitenant (Meta API)")
    loja = st.selectbox("Selecione a Operação", ["Parada Atlântida (Floripa)", "Casa da Limpeza (Antônio Carlos)"])
    
    if loja == "Parada Atlântida (Floripa)":
        st.info("Foco: Geolocalização & Cupons")
        st.button("Ver Próximos Posts Programados")
    else:
        st.info("Foco: B2B & Orçamentos")
        st.button("Disparar Tabela de Preços para Leads")

with tab_portal:
    st.subheader("🗺️ Portal Atlântida (Turismo & Cashback)")
    st.metric(label="Usuários Ativos", value="1,240")
    st.metric(label="Cashback Distribuído", value="R$ 3.450,00")
    if st.button("Gerar Relatório de Gamificação"):
        st.write("Análise de engajamento dos turistas gerada por IA.")

with tab_workspace:
    st.subheader("📬 Triagem Inteligente")
    st.write("**E-mails Urgentes (Resumo IA):**")
    st.warning("Fornecedor Casa da Limpeza solicitou ajuste de prazo.")
    st.write("**Agenda de Hoje:**")
    st.info("16:00 - Revisão de métricas de tráfego do Portal")
