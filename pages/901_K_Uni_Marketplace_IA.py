from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="K-Uni Marketplace IA",
    layout="wide",
)

st.title("K-Uni Marketplace de Solucoes em IA")
st.caption("Marketplace curado para aplicar IA em negocios reais, com diagnostico, implementacao assistida e governanca.")

st.markdown("""
# Pare de testar IA no escuro.

O K-Uni Marketplace organiza solucoes de IA por objetivo de negocio:

- vender mais
- produzir conteudo com consistencia
- automatizar atendimento
- criar funis
- gerar SaaS
- operar campanhas
- reduzir tarefas repetitivas

A proposta e simples: transformar ferramentas soltas em solucoes aplicaveis.
""")

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("IA para Vendas")
    st.write("Follow-up, propostas, CRM leve, scripts, qualificacao e atendimento comercial.")
    st.info("Ideal para consultores, prestadores e times comerciais.")

with c2:
    st.subheader("IA para Conteudo")
    st.write("Posts, roteiros, calendario editorial, copy, landing pages e criativos.")
    st.info("Ideal para criadores, social media e negocios locais.")

with c3:
    st.subheader("IA para Operacao")
    st.write("Dashboards, automacoes, relatorios, agentes internos e processos.")
    st.info("Ideal para empresas que querem ganhar eficiencia.")

st.divider()

st.header("Oferta de entrada")

left, right = st.columns([1.2, 1])

with left:
    st.markdown("""
## Diagnostico gratuito de IA aplicada

Receba um plano com **3 automacoes de IA** recomendadas para o seu negocio.

### Voce recebe:

1. Mapa rapido do seu processo atual.
2. Tres oportunidades de IA.
3. Prioridade por impacto e facilidade.
4. Sugestao de implementacao.
5. Proximo passo claro.
""")

with right:
    st.success("CTA: Quero meu diagnostico de IA")
    st.write("Status: rascunho local. Nenhum formulario real conectado ainda.")
    st.write("Proximo: conectar formulario local e approval gate.")

st.divider()

st.header("Pacotes iniciais")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.metric("Pacote", "Starter")
    st.write("Diagnostico + 1 automacao simples.")

with p2:
    st.metric("Pacote", "Growth")
    st.write("Funil + conteudo + automacao comercial.")

with p3:
    st.metric("Pacote", "Ops")
    st.write("Dashboard + agente interno + rotina operacional.")

with p4:
    st.metric("Pacote", "SaaS")
    st.write("Blueprint + prototipo + plano de validacao.")

st.divider()

st.header("Campanha Instagram V2")

campaign_path = PROJECT_ROOT / "content_packs" / "marketplace_ia" / "instagram_posts_v2.json"

if campaign_path.exists():
    posts = json.loads(campaign_path.read_text(encoding="utf-8"))
    for post in posts:
        with st.expander(post["title"]):
            st.write(post["caption"])
            st.code("\\n".join(post["hashtags"]), language="text")
else:
    st.info("Campanha V2 ainda nao encontrada.")

st.divider()

st.caption("Publicacao externa bloqueada. Esta pagina e um teste local supervisionado.")
