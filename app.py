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


def main() -> None:
    st.set_page_config(
        page_title="K-OS Local Command Center",
        page_icon="K",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_style()

    status = build_status()

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
