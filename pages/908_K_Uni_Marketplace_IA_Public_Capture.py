from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAPTURE_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "public_capture_queue.jsonl"

st.set_page_config(
    page_title="Solicitar Diagnostico IA | K-Uni",
    layout="wide",
)

st.title("Solicitar Diagnostico de IA")
st.caption("Captura publica controlada - teste local supervisionado.")

st.markdown("""
# Descubra 3 automacoes de IA para o seu negocio.

Preencha o formulario abaixo para simular a entrada de um lead publico.

Este teste salva os dados apenas localmente.
Nenhum WhatsApp, email, Instagram ou API externa sera acionado.
""")

st.divider()

left, right = st.columns([1.1, 1])

with left:
    st.subheader("O que voce recebe")
    st.write("- Mapeamento rapido do seu processo")
    st.write("- Tres oportunidades de automacao com IA")
    st.write("- Priorizacao por impacto e facilidade")
    st.write("- Sugestao de primeira implementacao")
    st.write("- Proximo passo comercial claro")

with right:
    with st.form("public_capture_form"):
        nome = st.text_input("Nome")
        contato = st.text_input("WhatsApp ou email")
        negocio = st.text_input("Nome do negocio")
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

        submitted = st.form_submit_button("Solicitar diagnostico")

        if submitted:
            CAPTURE_PATH.parent.mkdir(parents=True, exist_ok=True)

            lead = {
                "lead_id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "nome": nome,
                "contato": contato,
                "negocio": negocio,
                "segmento": segmento,
                "objetivo": objetivo,
                "desafio": desafio,
                "source": "public_capture_controlled_local",
                "status": "captured_public_local_only",
                "external_send_enabled": False,
                "human_review_required": True,
            }

            with CAPTURE_PATH.open("a", encoding="utf-8") as file:
                file.write(json.dumps(lead, ensure_ascii=False) + "\n")

            st.success("Solicitacao registrada localmente. Nenhum envio externo foi feito.")
            st.json({
                "lead_id": lead["lead_id"],
                "status": lead["status"],
                "external_send_enabled": lead["external_send_enabled"],
                "human_review_required": lead["human_review_required"],
            })

st.divider()

st.warning("Ambiente de teste local. Dados reais ficam em live/marketplace_ia/ e nao devem ir para GitHub.")

if CAPTURE_PATH.exists():
    total = len([line for line in CAPTURE_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()])
    st.metric("Capturas locais nesta fila", total)

st.caption("K-Uni Marketplace IA - captura publica controlada.")