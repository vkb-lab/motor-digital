from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from scripts.run_kos_local_home_status import build_status


ROOT = Path(__file__).resolve().parent
RECOMMENDED_PORT = 8501

OFFICIAL_CORE = [
    {
        "name": "KOS Operator Chat",
        "path": "pages/KOS_Operator_Chat.py",
        "route": "/KOS_Operator_Chat",
        "role": "Frontdoor conversational para pedidos naturais, diagnostico e resposta operacional.",
    },
    {
        "name": "KOS Unified Command Cockpit",
        "path": "pages/KOS_Unified_Command_Cockpit.py",
        "route": "/KOS_Unified_Command_Cockpit",
        "role": "Cockpit principal para comando, runtime, filas, auditoria e rotas seguras.",
    },
    {
        "name": "KOS Runtime Health",
        "path": "pages/KOS_Runtime_Health.py",
        "route": "/KOS_Runtime_Health",
        "role": "Leitura do estado operacional e do Git real/snapshotado.",
    },
    {
        "name": "KOS Mission Queue",
        "path": "pages/KOS_Mission_Queue.py",
        "route": "/KOS_Mission_Queue",
        "role": "Fila de missoes com aprovacao humana.",
    },
    {
        "name": "KOS Safe Execution Review",
        "path": "pages/KOS_Safe_Execution_Review.py",
        "route": "/KOS_Safe_Execution_Review",
        "role": "Revisao de execucao segura antes de qualquer rota sensivel.",
    },
    {
        "name": "KOS Approval Gate / Human Approval",
        "path": "pages/KOS_Human_Approval.py",
        "route": "/KOS_Human_Approval",
        "role": "Console de aprovacao humana auditavel.",
    },
    {
        "name": "KOS Gmail Status",
        "path": "reports/KOS_GMAIL_REAL_CONNECTION_STATUS.md",
        "route": "",
        "role": "Card read-only local; nenhuma chamada Gmail API e nenhum conteudo de email.",
    },
    {
        "name": "KOS Google Toolbelt Status",
        "path": "memory/kos_governance/KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json",
        "route": "",
        "role": "Card read-only do registry do Google AI Toolbelt.",
    },
    {
        "name": "KOS Brain Provider Status",
        "path": "memory/kos_governance/KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json",
        "route": "",
        "role": "Card read-only da prioridade de provedores de cerebro.",
    },
    {
        "name": "KOS Render Read-Only Mobile Runtime",
        "path": "app_render.py",
        "route": "",
        "role": "Referencia ao runtime cloud read-only, sem virar home local.",
    },
]

LEGACY_GROUPS = [
    "Series K-Atlas numeradas e stubs de batch factory",
    "Series K-Uni e Marketplace IA",
    "Command Centers antigos substituidos pelo Unified Command Cockpit",
    "Approval gates duplicados",
    "Paginas K-OS core granulares de checkpoints antigos",
]

OFFICIAL_NAVIGATION = [
    {
        "label": "Entrar no Operator Chat",
        "name": "KOS Operator Chat",
        "path": "pages/KOS_Operator_Chat.py",
        "href": "/KOS_Operator_Chat",
        "description": "Frontdoor operacional do K-OS: intenção, roteamento, Gmail, Toolbelt, Brain, sequências e Human Gate.",
        "primary": True,
    },
    {
        "label": "Abrir Unified Command Cockpit",
        "name": "Unified Command Cockpit",
        "path": "pages/KOS_Unified_Command_Cockpit.py",
        "href": "/KOS_Unified_Command_Cockpit",
        "description": "Cockpit consolidado para comando local, filas, runtime e evidência.",
    },
    {
        "label": "Ver Mission Queue",
        "name": "Mission Queue",
        "path": "pages/KOS_Mission_Queue.py",
        "href": "/KOS_Mission_Queue",
        "description": "Fila de missões e próximos passos governados.",
    },
    {
        "label": "Abrir Human Approval",
        "name": "Human Approval",
        "path": "pages/KOS_Human_Approval.py",
        "href": "/KOS_Human_Approval",
        "description": "Gate humano para decisões sensíveis.",
    },
    {
        "label": "Ver Runtime Health",
        "name": "Runtime Health",
        "path": "pages/KOS_Runtime_Health.py",
        "href": "/KOS_Runtime_Health",
        "description": "Saúde operacional local e estado de execução.",
    },
    {
        "label": "Ver Gmail Status",
        "name": "Gmail Status",
        "path": "reports/KOS_GMAIL_REAL_CONNECTION_STATUS.md",
        "href": "",
        "description": "Status local/read-only, sem chamada Gmail API.",
    },
    {
        "label": "Ver Google Toolbelt",
        "name": "Google Toolbelt",
        "path": "memory/kos_governance/KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json",
        "href": "",
        "description": "Registry local das ferramentas Google subordinadas.",
    },
    {
        "label": "Ver Brain Provider",
        "name": "Brain Provider",
        "path": "memory/kos_governance/KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json",
        "href": "",
        "description": "Prioridade local de cérebro/provedor.",
    },
    {
        "label": "Abrir Reports/Evidence",
        "name": "Reports/Evidence",
        "path": "reports/",
        "href": "",
        "description": "Evidências locais e relatórios auditáveis.",
    },
]


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1160px;
            padding-top: 1.5rem;
        }
        .kos-hero, .kos-card, .kos-warning {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 1rem;
        }
        .kos-hero {
            border-left: 4px solid #245bdb;
            margin-bottom: 1rem;
        }
        .kos-warning {
            border-left: 4px solid #9a6700;
            background: #fffaf0;
            margin: 1rem 0;
        }
        .kos-muted {
            color: #667085;
        }
        .kos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 0.75rem;
            margin: 0.75rem 0 1rem;
        }
        .kos-nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 0.75rem;
            margin: 1rem 0 1.25rem;
        }
        .kos-nav-action {
            display: block;
            min-height: 126px;
            border: 1px solid #cfd8e6;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.95rem;
            color: #172033 !important;
            text-decoration: none !important;
        }
        .kos-nav-action:hover {
            border-color: #245bdb;
            box-shadow: 0 8px 24px rgba(20, 36, 64, 0.08);
        }
        .kos-nav-action.primary {
            border: 2px solid #245bdb;
            background: #f3f7ff;
            min-height: 154px;
        }
        .kos-nav-label {
            display: block;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }
        .kos-nav-desc {
            display: block;
            color: #667085;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .kos-card-title {
            font-weight: 750;
            margin-bottom: 0.35rem;
        }
        .kos-card-meta {
            color: #667085;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        .kos-chip {
            display: inline-block;
            border: 1px solid #d8dee8;
            border-radius: 999px;
            padding: 0.18rem 0.5rem;
            margin: 0.1rem 0.15rem 0.1rem 0;
            font-size: 0.78rem;
            color: #172033;
            background: #f8fafc;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] a {
            text-decoration: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def html_escape(value: Any) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def status_badge(ok: bool) -> str:
    return "found" if ok else "missing"


def render_core_card(item: dict[str, str], status: dict[str, Any]) -> None:
    path = item["path"]
    exists = bool(status["core_paths"].get(path, {}).get("exists"))
    route = item.get("route", "")
    badge = status_badge(exists)

    if route and exists:
        title = f"<a href='{html_escape(route)}' target='_self'>{html_escape(item['name'])}</a>"
    else:
        title = html_escape(item["name"])

    st.markdown(
        f"""
        <section class="kos-card">
          <div class="kos-card-title">{title}</div>
          <div class="kos-card-meta">{html_escape(item["role"])}</div>
          <div>
            <span class="kos-chip">{badge}</span>
            <span class="kos-chip">{html_escape(path)}</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_json_expander(label: str, payload: dict[str, Any]) -> None:
    with st.expander(label, expanded=False):
        st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")


def render_official_navigation(status: dict[str, Any]) -> None:
    st.subheader("Navegação oficial K-OS")
    st.markdown(
        """
        <section class="kos-warning">
          <div class="kos-card-title">Páginas legadas em modo avançado</div>
          <div class="kos-card-meta">
            A navegação automática gigante do Streamlit foi reduzida visualmente nesta home.
            As páginas legadas continuam existindo no diretório pages/ e não foram movidas nem deletadas.
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    cards = ['<div class="kos-nav-grid">']
    for item in OFFICIAL_NAVIGATION:
        path = item["path"]
        exists = path.endswith("/") or bool(status["core_paths"].get(path, {}).get("exists")) or (ROOT / path).exists()
        href = item.get("href") or "#"
        classes = "kos-nav-action primary" if item.get("primary") else "kos-nav-action"
        badge = "found" if exists else "read-only"
        cards.append(
            f"""
            <a class="{classes}" href="{html_escape(href)}" target="_self">
              <span class="kos-nav-label">{html_escape(item["label"])}</span>
              <span class="kos-nav-desc">{html_escape(item["description"])}</span>
              <span class="kos-chip">{html_escape(item["name"])}</span>
              <span class="kos-chip">{badge}</span>
            </a>
            """
        )
    cards.append("</div>")
    st.markdown("\n".join(cards), unsafe_allow_html=True)


def render_official_sidebar() -> None:
    with st.sidebar:
        st.markdown("### Navegação oficial K-OS")
        st.markdown("[Entrar no Operator Chat](/KOS_Operator_Chat)")
        st.markdown("[Unified Command Cockpit](/KOS_Unified_Command_Cockpit)")
        st.markdown("[Mission Queue](/KOS_Mission_Queue)")
        st.markdown("[Human Approval](/KOS_Human_Approval)")
        st.markdown("[Runtime Health](/KOS_Runtime_Health)")
        st.caption("Legado/avançado: páginas antigas seguem no diretório pages/, mas fora da navegação oficial desta home.")


def main() -> None:
    st.set_page_config(
        page_title="K-OS Local Command Center",
        page_icon="K",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_style()

    status = build_status()
    render_official_sidebar()

    st.title("K-OS Local Command Center")
    st.markdown(
        """
        <section class="kos-hero">
          <div class="kos-card-title">Nucleo soberano local</div>
          <div class="kos-card-meta">
            Esta e a home oficial local do K-OS. Ela consolida o centro de comando sem executar Gmail,
            sem publicar, sem deploy e sem automatizar acoes externas.
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Branch atual", status["git"].get("branch") or "unknown")
    col2.metric("Git status real", "sujo" if status["git"].get("dirty") else "limpo")
    col3.metric("Porta recomendada", str(RECOMMENDED_PORT))
    col4.metric("Nucleos encontrados", f"{status['summary']['core_found']}/{status['summary']['core_total']}")

    if status["git"].get("status_short"):
        st.caption("Git status real:")
        st.code(status["git"]["status_short"], language="text")
    else:
        st.caption("Git status real: workspace limpo.")

    render_official_navigation(status)

    st.subheader("Nucleo oficial")
    st.markdown('<div class="kos-grid">', unsafe_allow_html=True)
    for item in OFFICIAL_CORE:
        render_core_card(item, status)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Status dos blocos principais")
    block_rows = [
        {
            "bloco": block["name"],
            "status": status_badge(block["exists"]),
            "path": block["path"],
            "tipo": block["kind"],
        }
        for block in status["blocks"]
    ]
    st.dataframe(block_rows, use_container_width=True, hide_index=True)

    st.subheader("Modulos avancados / legado")
    st.markdown(
        """
        <section class="kos-warning">
          <div class="kos-card-title">Sidebar automatico ainda mostra paginas legadas</div>
          <div class="kos-card-meta">
            O Streamlit ainda lista automaticamente a pasta pages. Nenhuma pagina foi deletada nesta fase.
            A proxima etapa recomendada e custom navigation ou migracao controlada para ocultar o legado
            sem quebrar URLs existentes.
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    for group in LEGACY_GROUPS:
        st.write(f"- {group}")

    st.subheader("Proxima etapa recomendada")
    st.write(
        "Implementar custom navigation governada para expor somente o nucleo oficial e mover o restante para busca/diagnostico legado."
    )

    render_json_expander("JSON sanitizado da home", status)


if __name__ == "__main__":
    main()
