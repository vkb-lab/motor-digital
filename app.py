"""
Motor Digital Multitenant — v2.0
Inteligência Central: Gemini 1.5 Pro via Google AI Studio
Autor: vkb-lab | Engenharia de Software
"""

import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, date

# ─────────────────────────────────────────────
# CONFIGURAÇÃO GLOBAL DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Motor Digital",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CSS mobile-friendly e tema escuro personalizado
st.markdown("""
<style>
    /* Tipografia e espaçamento mobile */
    .block-container { padding: 1rem 1rem 2rem 1rem; max-width: 480px; }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }

    /* Cartões de métricas */
    div[data-testid="metric-container"] {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* Botões */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1rem;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.4rem 0.6rem;
        font-size: 0.82rem;
    }

    /* Badge de status */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-online  { background: #a6e3a1; color: #1e1e2e; }
    .badge-warning { background: #f9e2af; color: #1e1e2e; }
    .badge-offline { background: #f38ba8; color: #1e1e2e; }

    /* Separadores */
    hr { border-color: #313244; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# UTILITÁRIOS — GEMINI 1.5 PRO
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-pro:generateContent"
)


def gemini_chat(prompt: str, system_context: str = "") -> str:
    """Envia prompt ao Gemini 1.5 Pro e retorna a resposta em texto."""
    if not GEMINI_API_KEY:
        return (
            "⚠️ Chave da API Gemini não configurada. "
            "Defina a variável de ambiente `GEMINI_API_KEY`."
        )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{system_context}\n\n{prompt}".strip()}
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        },
    }
    try:
        resp = requests.post(
            f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.Timeout:
        return "⏱️ Tempo de resposta excedido. Tente novamente."
    except Exception as exc:
        return f"❌ Erro ao consultar Gemini: {exc}"


# ─────────────────────────────────────────────
# DADOS MOCK — SIMULAÇÃO DE MÉTRICAS
# ─────────────────────────────────────────────
def get_painel_metrics() -> dict:
    return {
        "leads_hoje": 142,
        "leads_delta": "+22%",
        "receita_semana": "R$ 18.450",
        "receita_delta": "+8%",
        "tarefas_pendentes": 7,
        "tarefas_delta": "-3",
        "uptime_ia": "99,8%",
    }


def get_meta_posts(loja: str) -> pd.DataFrame:
    if loja == "Parada Atlântida":
        return pd.DataFrame({
            "Data/Hora": ["22/05 14:00", "23/05 10:00", "24/05 18:30"],
            "Formato": ["Reels", "Carrossel", "Story"],
            "Tema": ["Promoção Feriado", "Cardápio Novo", "Cupom Flash"],
            "Status": ["✅ Agendado", "✅ Agendado", "⏳ Rascunho"],
        })
    else:
        return pd.DataFrame({
            "Data/Hora": ["22/05 09:00", "23/05 15:00", "25/05 11:00"],
            "Formato": ["Post Feed", "Story", "Reels"],
            "Tema": ["Tabela B2B", "Depoimento Cliente", "Processo de Limpeza"],
            "Status": ["✅ Agendado", "⏳ Rascunho", "✅ Agendado"],
        })


def get_portal_metrics() -> dict:
    return {
        "usuarios_ativos": "1.240",
        "cashback_total": "R$ 3.450",
        "parceiros": 18,
        "resgates_mes": 312,
    }


def get_agenda_hoje() -> list[dict]:
    return [
        {"hora": "09:30", "evento": "Reunião Meta Ads — Parada Atlântida", "tipo": "🔵"},
        {"hora": "11:00", "evento": "Revisão de conteúdo — Casa da Limpeza", "tipo": "🟢"},
        {"hora": "14:00", "evento": "Call com parceiro Portal Atlântida", "tipo": "🟡"},
        {"hora": "16:00", "evento": "Análise de métricas de tráfego", "tipo": "🔵"},
    ]


def get_emails_mock() -> list[dict]:
    return [
        {
            "remetente": "fornecedor@casadalimpeza.com.br",
            "assunto": "Ajuste de prazo — pedido #4821",
            "urgencia": "🔴 Urgente",
            "resumo": "Fornecedor solicita confirmação de novo prazo de entrega até sexta-feira.",
        },
        {
            "remetente": "parceiro@portalatlantica.com.br",
            "assunto": "Proposta de campanha cashback — junho",
            "urgencia": "🟡 Normal",
            "resumo": "Parceiro propõe campanha especial de cashback para o período junino.",
        },
        {
            "remetente": "ads@meta.com",
            "assunto": "Relatório semanal de performance",
            "urgencia": "🟢 Informativo",
            "resumo": "CPM médio caiu 12% na semana. CTR de Stories subiu para 3,4%.",
        },
    ]


# ─────────────────────────────────────────────
# CABEÇALHO PRINCIPAL
# ─────────────────────────────────────────────
col_logo, col_status = st.columns([3, 1])
with col_logo:
    st.markdown("## ⚡ Motor Digital")
    st.caption("Sistema Multitenant · Gemini 1.5 Pro")
with col_status:
    st.markdown(
        '<span class="status-badge badge-online">● ONLINE</span>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS PRINCIPAIS
# ─────────────────────────────────────────────
tab_painel, tab_meta, tab_portal, tab_workspace = st.tabs([
    "🏠 Painel",
    "📣 Meta Ops",
    "🌐 Portal",
    "🗂️ Workspace",
])


# ══════════════════════════════════════════════
# ABA 1 — PAINEL GERAL
# ══════════════════════════════════════════════
with tab_painel:
    st.subheader("Painel Geral")
    metrics = get_painel_metrics()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Leads Hoje", metrics["leads_hoje"], metrics["leads_delta"])
        st.metric("Tarefas Pendentes", metrics["tarefas_pendentes"], metrics["tarefas_delta"])
    with c2:
        st.metric("Receita Semana", metrics["receita_semana"], metrics["receita_delta"])
        st.metric("Uptime IA", metrics["uptime_ia"])

    st.markdown("---")
    st.subheader("🤖 Assistente Gemini")
    st.caption("Consulte a inteligência central do sistema.")

    pergunta = st.text_area(
        "Sua pergunta ou instrução:",
        placeholder="Ex: Quais ações de marketing devo priorizar esta semana?",
        height=100,
        key="painel_pergunta",
    )
    if st.button("Consultar Gemini 1.5 Pro", key="btn_painel_gemini"):
        if pergunta.strip():
            with st.spinner("Gemini processando..."):
                ctx = (
                    "Você é o assistente central do Motor Digital Multitenant. "
                    "Responda de forma objetiva e estratégica para um gestor de negócios digitais."
                )
                resposta = gemini_chat(pergunta, system_context=ctx)
            st.success("Resposta da IA:")
            st.write(resposta)
        else:
            st.warning("Digite uma pergunta antes de consultar.")

    st.markdown("---")
    st.subheader("📊 Resumo de Operações")
    resumo_df = pd.DataFrame({
        "Operação": ["Parada Atlântida", "Casa da Limpeza", "Portal Atlântida"],
        "Status": ["✅ Ativa", "✅ Ativa", "✅ Ativa"],
        "Posts Agendados": [3, 2, 1],
        "Leads 7d": [89, 53, 0],
    })
    st.dataframe(resumo_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# ABA 2 — OPERAÇÕES META (PARADA ATLÂNTIDA / CASA DA LIMPEZA)
# ══════════════════════════════════════════════
with tab_meta:
    st.subheader("Operações Meta")
    st.caption("Gestão de conteúdo e anúncios para as duas operações.")

    loja_sel = st.radio(
        "Selecione a operação:",
        ["Parada Atlântida", "Casa da Limpeza"],
        horizontal=True,
        key="meta_loja",
    )

    if loja_sel == "Parada Atlântida":
        st.markdown("**🏖️ Parada Atlântida** · Turismo & Gastronomia · Florianópolis")
        st.info("Foco: Geolocalização, cupons flash e conteúdo de experiência.")
    else:
        st.markdown("**🧹 Casa da Limpeza** · Produtos de Higiene B2B · Antônio Carlos")
        st.info("Foco: Tabelas de preço B2B, depoimentos e orçamentos automatizados.")

    st.markdown("##### 📅 Posts Programados")
    posts_df = get_meta_posts(loja_sel)
    st.dataframe(posts_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📤 Disparar Tabela de Preços", key="btn_tabela"):
            st.success("Tabela de preços enviada para leads qualificados.")
    with col_b2:
        if st.button("📆 Ver Calendário Completo", key="btn_cal"):
            st.info("Integração com Meta Business Suite em configuração.")

    st.markdown("---")
    st.subheader("✍️ Gerador de Legenda com IA")
    tema_post = st.text_input(
        "Tema do post:",
        placeholder=f"Ex: Promoção de fim de semana — {loja_sel}",
        key="meta_tema",
    )
    tom_voz = st.selectbox(
        "Tom de voz:",
        ["Descontraído", "Profissional", "Urgente / Oferta", "Inspirador"],
        key="meta_tom",
    )
    if st.button("Gerar Legenda com Gemini", key="btn_meta_legenda"):
        if tema_post.strip():
            with st.spinner("Criando legenda..."):
                ctx = (
                    f"Você é um copywriter especialista em redes sociais para a operação '{loja_sel}'. "
                    f"Crie uma legenda para Instagram com tom '{tom_voz}', "
                    "com até 150 palavras, incluindo emojis e hashtags relevantes."
                )
                legenda = gemini_chat(tema_post, system_context=ctx)
            st.success("Legenda gerada:")
            st.write(legenda)
        else:
            st.warning("Informe o tema do post.")


# ══════════════════════════════════════════════
# ABA 3 — PORTAL ATLÂNTIDA (TURISMO / CASHBACK)
# ══════════════════════════════════════════════
with tab_portal:
    st.subheader("Portal Atlântida")
    st.caption("Plataforma de turismo, gamificação e cashback.")

    metrics_p = get_portal_metrics()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Usuários Ativos", metrics_p["usuarios_ativos"])
        st.metric("Parceiros Cadastrados", metrics_p["parceiros"])
    with c2:
        st.metric("Cashback Distribuído", metrics_p["cashback_total"])
        st.metric("Resgates no Mês", metrics_p["resgates_mes"])

    st.markdown("---")
    st.subheader("🏆 Ranking de Gamificação")
    ranking_df = pd.DataFrame({
        "Posição": ["🥇 1º", "🥈 2º", "🥉 3º", "4º", "5º"],
        "Usuário": ["Carlos M.", "Ana P.", "João S.", "Marta L.", "Pedro R."],
        "Pontos": [4820, 3910, 3450, 2980, 2710],
        "Cashback": ["R$ 48,20", "R$ 39,10", "R$ 34,50", "R$ 29,80", "R$ 27,10"],
    })
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📍 Parceiros em Destaque")
    parceiros_df = pd.DataFrame({
        "Parceiro": ["Pousada Beira-Mar", "Restaurante Maré Alta", "Surf Shop Atlântida"],
        "Categoria": ["Hospedagem", "Gastronomia", "Esportes"],
        "Cashback Oferecido": ["8%", "5%", "10%"],
        "Avaliação": ["⭐ 4.8", "⭐ 4.6", "⭐ 4.9"],
    })
    st.dataframe(parceiros_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📈 Relatório de Engajamento com IA")
    periodo = st.selectbox(
        "Período de análise:",
        ["Últimos 7 dias", "Últimos 30 dias", "Este trimestre"],
        key="portal_periodo",
    )
    if st.button("Gerar Análise com Gemini", key="btn_portal_relatorio"):
        with st.spinner("Analisando dados do portal..."):
            ctx = (
                "Você é analista de dados do Portal Atlântida, plataforma de turismo e cashback. "
                "Gere um relatório executivo de engajamento com insights e recomendações estratégicas."
            )
            prompt_rel = (
                f"Período: {periodo}. "
                f"Usuários ativos: {metrics_p['usuarios_ativos']}. "
                f"Cashback distribuído: {metrics_p['cashback_total']}. "
                f"Parceiros: {metrics_p['parceiros']}. "
                f"Resgates: {metrics_p['resgates_mes']}. "
                "Forneça análise e próximos passos."
            )
            relatorio = gemini_chat(prompt_rel, system_context=ctx)
        st.success("Relatório gerado:")
        st.write(relatorio)


# ══════════════════════════════════════════════
# ABA 4 — WORKSPACE (GMAIL / AGENDA)
# ══════════════════════════════════════════════
with tab_workspace:
    st.subheader("Workspace")
    st.caption("Triagem inteligente de e-mails e agenda do dia.")

    # ── E-mails ──
    st.markdown("#### 📬 Caixa de Entrada — Triagem IA")
    emails = get_emails_mock()
    for email in emails:
        with st.expander(f"{email['urgencia']}  {email['assunto']}"):
            st.markdown(f"**De:** `{email['remetente']}`")
            st.markdown(f"**Resumo IA:** {email['resumo']}")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("✉️ Redigir Resposta", key=f"resp_{email['remetente']}"):
                    with st.spinner("Gemini redigindo resposta..."):
                        ctx = (
                            "Você é assistente executivo. Redija uma resposta profissional "
                            "e objetiva para o e-mail descrito."
                        )
                        resposta_email = gemini_chat(
                            f"E-mail recebido: {email['assunto']}. Contexto: {email['resumo']}",
                            system_context=ctx,
                        )
                    st.write(resposta_email)
            with col_r2:
                if st.button("🗑️ Arquivar", key=f"arq_{email['remetente']}"):
                    st.info("E-mail arquivado.")

    st.markdown("---")

    # ── Agenda ──
    st.markdown(f"#### 📅 Agenda — {date.today().strftime('%d/%m/%Y')}")
    agenda = get_agenda_hoje()
    for item in agenda:
        st.markdown(
            f"{item['tipo']} **{item['hora']}** — {item['evento']}"
        )

    st.markdown("---")
    st.subheader("➕ Criar Novo Evento com IA")
    descricao_evento = st.text_input(
        "Descreva o evento:",
        placeholder="Ex: Reunião de alinhamento com equipe de marketing",
        key="ws_evento",
    )
    if st.button("Sugerir Horário e Pauta com Gemini", key="btn_ws_evento"):
        if descricao_evento.strip():
            with st.spinner("Gemini organizando agenda..."):
                ctx = (
                    "Você é assistente de produtividade. Sugira o melhor horário para o evento, "
                    "uma pauta estruturada e duração estimada."
                )
                sugestao = gemini_chat(descricao_evento, system_context=ctx)
            st.success("Sugestão da IA:")
            st.write(sugestao)
        else:
            st.warning("Descreva o evento antes de continuar.")

    st.markdown("---")
    st.subheader("🔗 Integrações")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown(
            '<span class="status-badge badge-warning">⚙ Gmail API</span>',
            unsafe_allow_html=True,
        )
        st.caption("Configuração pendente")
    with col_i2:
        st.markdown(
            '<span class="status-badge badge-warning">⚙ Google Calendar</span>',
            unsafe_allow_html=True,
        )
        st.caption("Configuração pendente")


# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"Motor Digital Multitenant · v2.0 · "
    f"Powered by Gemini 1.5 Pro · "
    f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
)
