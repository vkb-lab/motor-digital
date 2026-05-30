from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEADS_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "lead_intake.jsonl"
POSTS_PATH = PROJECT_ROOT / "content_packs" / "marketplace_ia" / "instagram_posts_v2.json"

st.set_page_config(page_title="K-Uni Marketplace IA", layout="wide")

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

st.header("Diagnostico gratuito de IA aplicada")

left, right = st.columns([1.1, 1])

with left:
    st.markdown("""
Receba um plano com **3 automacoes de IA** recomendadas para o seu negocio.

### Voce recebe:

1. Mapa rapido do seu processo atual.
2. Tres oportunidades de IA.
3. Prioridade por impacto e facilidade.
4. Sugestao de implementacao.
5. Proximo passo claro.
""")

with right:
    with st.form("marketplace_ia_lead_form"):
        st.subheader("Solicitar diagnostico")

        nome = st.text_input("Seu nome")
        negocio = st.text_input("Nome do negocio")
        contato = st.text_input("WhatsApp ou email")
        segmento = st.selectbox(
            "Segmento",
            [
                "Negocio local",
                "Consultoria",
                "Prestador de servico",
                "Criador de conteudo",
                "E-commerce",
                "SaaS",
                "Outro",
            ],
        )
        objetivo = st.selectbox(
            "Objetivo principal",
            [
                "Vender mais",
                "Economizar tempo",
                "Criar conteudo",
                "Automatizar atendimento",
                "Criar um SaaS",
                "Organizar operacao",
            ],
        )
        desafio = st.text_area("Qual tarefa mais toma tempo hoje?")

        submitted = st.form_submit_button("Quero meu diagnostico")

        if submitted:
            LEADS_PATH.parent.mkdir(parents=True, exist_ok=True)

            lead = {
                "lead_id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "nome": nome,
                "negocio": negocio,
                "contato": contato,
                "segmento": segmento,
                "objetivo": objetivo,
                "desafio": desafio,
                "source": "marketplace_ia_local_test",
                "status": "captured_local_only",
                "external_send_enabled": False,
                "human_review_required": True,
            }

            with LEADS_PATH.open("a", encoding="utf-8") as file:
                file.write(json.dumps(lead, ensure_ascii=False) + "\n")

            st.success("Lead salvo localmente. Nenhum envio externo foi feito.")
            st.json(lead)

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

if POSTS_PATH.exists():
    posts = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    for post in posts:
        with st.expander(post["title"]):
            st.write(post["caption"])
            st.code("\n".join(post["hashtags"]), language="text")
else:
    st.info("Campanha V2 ainda nao encontrada.")

st.divider()

st.caption("Publicacao externa bloqueada. Esta pagina e um teste local supervisionado.")
