from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Marketplace IA | K-Uni",
    layout="wide",
)

st.title("Marketplace IA")
st.caption("Solucoes praticas de inteligencia artificial para negocios reais.")

st.markdown("""
# Transforme IA em resultado operacional.

O Marketplace IA ajuda empresas, criadores e prestadores de servico a identificar,
priorizar e implementar automacoes de inteligencia artificial com seguranca,
governanca e acompanhamento humano.

Sem promessas magicas. Sem ferramenta solta. Apenas aplicacao pratica.
""")

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("IA para Vendas")
    st.write("Organize leads, follow-ups, propostas e atendimento comercial com fluxos assistidos por IA.")

with c2:
    st.subheader("IA para Conteudo")
    st.write("Crie campanhas, posts, roteiros, landing pages e calendarios editoriais com aprovacao humana.")

with c3:
    st.subheader("IA para Operacoes")
    st.write("Automatize tarefas repetitivas, relatórios, dashboards e rotinas internas.")

st.divider()

st.header("Oferta de entrada")

left, right = st.columns([1.2, 1])

with left:
    st.markdown("""
## Diagnostico de IA Aplicada

Receba um plano simples com:

1. Mapeamento rapido do processo atual.
2. Tres oportunidades de automacao com IA.
3. Priorizacao por impacto e facilidade.
4. Sugestao de primeira implementacao.
5. Proximo passo claro para execucao.
""")

with right:
    st.success("CTA publico: Solicitar diagnostico")
    st.write("Status: landing publica sanitizada.")
    st.write("Dados reais nao sao carregados nesta pagina.")

st.divider()

st.header("Pacotes")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.metric("Starter", "Diagnostico")
    st.write("Mapa de oportunidades e primeira automacao sugerida.")

with p2:
    st.metric("Growth", "Funil IA")
    st.write("Conteudo, captação, follow-up e proposta comercial.")

with p3:
    st.metric("Ops", "Operacao IA")
    st.write("Dashboard, agente interno e automacoes de rotina.")

with p4:
    st.metric("SaaS", "MVP IA")
    st.write("Blueprint, prototipo e plano de validacao.")

st.divider()

st.header("Como funciona")

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.subheader("1. Diagnostico")
    st.write("Entendemos o processo e o objetivo.")

with s2:
    st.subheader("2. Priorizacao")
    st.write("Selecionamos as automacoes com maior impacto.")

with s3:
    st.subheader("3. Implementacao")
    st.write("Criamos o primeiro fluxo com seguranca.")

with s4:
    st.subheader("4. Operacao")
    st.write("Acompanhamos melhorias e proximos passos.")

st.divider()

st.warning("Esta e uma landing publica sanitizada. Nenhum dado de lead, proposta ou operacao local e exibido.")

st.caption("K-Uni Marketplace IA - versao publica inicial.")