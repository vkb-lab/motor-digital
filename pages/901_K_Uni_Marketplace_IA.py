from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="K-Uni Marketplace IA",
    layout="wide",
)

st.title("K-Uni Marketplace de Solucoes em IA")
st.caption("Teste real 001 - pagina comercial gerada pelo K-Uni Local OS.")

st.markdown("""
## Solucoes de IA prontas para acelerar negocios

Um marketplace curado para empresas, criadores e profissionais que querem aplicar IA sem perder tempo com complexidade tecnica.

Encontre solucoes para:

- atendimento automatizado
- criacao de conteudo
- automacao comercial
- analise de dados
- funis de venda
- criacao de SaaS
- campanhas para Instagram e WhatsApp
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("IA para Vendas")
    st.write("Scripts, follow-up, CRM leve, propostas e atendimento.")
    st.button("Ver solucoes de vendas", disabled=True)

with col2:
    st.subheader("IA para Conteudo")
    st.write("Posts, roteiros, landing pages, criativos e calendario editorial.")
    st.button("Ver solucoes de conteudo", disabled=True)

with col3:
    st.subheader("IA para Operacoes")
    st.write("Automacoes, dashboards, relatorios e agentes internos.")
    st.button("Ver solucoes de operacao", disabled=True)

st.divider()

st.header("Oferta inicial")

st.success("Diagnostico gratuito: descubra 3 automacoes de IA que podem economizar tempo ou gerar receita no seu negocio.")

st.markdown("""
### Como funciona

1. Voce informa seu tipo de negocio.
2. O K-Uni analisa oportunidades de IA.
3. Recebe um plano simples com 3 solucoes recomendadas.
4. Pode escolher implementar com suporte assistido.

### Chamada principal

**Pare de testar IA no escuro. Comece com um plano pratico para seu negocio.**
""")

st.divider()

st.header("Campanha Instagram - rascunho")

campaign_path = PROJECT_ROOT / "content_packs" / "marketplace_ia" / "instagram_posts.json"

if campaign_path.exists():
    posts = json.loads(campaign_path.read_text(encoding="utf-8"))
    for post in posts:
        with st.expander(post["title"]):
            st.write(post["caption"])
            st.code("\\n".join(post["hashtags"]), language="text")
else:
    st.info("Campanha ainda nao encontrada.")

st.divider()

st.caption("Publicacao externa bloqueada. Esta pagina e apenas um teste local supervisionado.")
