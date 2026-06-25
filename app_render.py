from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


ROOT = Path(__file__).resolve().parent

GMAIL_STATUS_REPORT = ROOT / "reports" / "KOS_GMAIL_REAL_CONNECTION_STATUS.md"
GOOGLE_TOOLBELT_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json"
BRAIN_PROVIDER_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json"
BROWSER_AUDIT = ROOT / "reports" / "KOS_CODEX_BROWSER_AUDIT_20260625_092134.md"
RENDER_AUDIT = ROOT / "reports" / "KOS_RENDER_CLOUD_RUNTIME_AUDIT_20260625_095054.md"


st.set_page_config(
    page_title="K-OS Cloud Status",
    page_icon="K",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --kos-ink: #172033;
            --kos-muted: #667085;
            --kos-line: #d8dee8;
            --kos-panel: #ffffff;
            --kos-surface: #f4f7fb;
            --kos-ok: #12715f;
            --kos-warn: #9a6700;
            --kos-blue: #245bdb;
        }

        .stApp {
            background: var(--kos-surface);
            color: var(--kos-ink);
        }

        .block-container {
            max-width: 760px;
            padding: 1.1rem 1rem 3rem;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--kos-ink);
        }

        h1 {
            font-size: 2.05rem;
            margin-bottom: 0.2rem;
        }

        .kos-banner, .kos-card {
            background: var(--kos-panel);
            border: 1px solid var(--kos-line);
            border-radius: 8px;
            padding: 1rem;
            margin: 0.75rem 0;
        }

        .kos-banner {
            border-left: 4px solid var(--kos-blue);
        }

        .kos-card.ok {
            border-left: 4px solid var(--kos-ok);
        }

        .kos-card.warn {
            border-left: 4px solid var(--kos-warn);
        }

        .kos-label {
            color: var(--kos-muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .kos-title {
            font-size: 1.05rem;
            font-weight: 760;
            margin-bottom: 0.35rem;
        }

        .kos-text {
            color: var(--kos-muted);
            line-height: 1.5;
            font-size: 0.94rem;
        }

        .kos-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.65rem;
        }

        .kos-chip {
            border: 1px solid var(--kos-line);
            background: #f8fafc;
            border-radius: 999px;
            padding: 0.28rem 0.62rem;
            font-size: 0.82rem;
            color: var(--kos-ink);
        }

        @media (max-width: 520px) {
            .block-container {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            h1 {
                font-size: 1.7rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_text(path: Path, limit: int = 6000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def first_matching_line(text: str, markers: tuple[str, ...]) -> str:
    for line in text.splitlines():
        clean = line.strip(" -")
        lower = clean.lower()
        if clean and any(marker in lower for marker in markers):
            return clean[:220]
    return ""


def markdown_signal(path: Path, markers: tuple[str, ...]) -> dict[str, str]:
    text = read_text(path)
    return {
        "state": "found" if text else "missing",
        "signal": first_matching_line(text, markers) if text else "Arquivo nao encontrado no snapshot cloud.",
    }


def card(title: str, state: str, body: str, chips: list[str] | None = None) -> None:
    kind = "ok" if state == "found" else "warn"
    chip_html = ""
    if chips:
        chip_html = "<div class='kos-chip-row'>" + "".join(f"<span class='kos-chip'>{chip}</span>" for chip in chips) + "</div>"
    st.markdown(
        f"""
        <section class="kos-card {kind}">
          <div class="kos-label">{state}</div>
          <div class="kos-title">{title}</div>
          <div class="kos-text">{body}</div>
          {chip_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def gmail_status() -> tuple[str, str, list[str]]:
    text = read_text(GMAIL_STATUS_REPORT, limit=2200)
    if not text:
        return "missing", "Relatorio Gmail real nao encontrado no snapshot cloud. Nenhum email e exibido.", ["read-only"]
    status_line = first_matching_line(text, ("status", "gmail", "connected", "conectado", "token"))
    body = status_line or "Relatorio Gmail real encontrado. Conteudo de mensagens permanece oculto neste painel."
    return "found", body, ["sem emails", "sem snippets", "sem API"]


def google_toolbelt_status() -> tuple[str, str, list[str]]:
    data = read_json(GOOGLE_TOOLBELT_REGISTRY)
    if not data:
        return "missing", "Registry do Google AI Toolbelt nao encontrado.", ["registry"]
    tools = data.get("tools", [])
    categories = sorted({str(item.get("category", "")).strip() for item in tools if isinstance(item, dict) and item.get("category")})
    body = f"Registry carregado: {data.get('status', 'status desconhecido')}. Ferramentas registradas: {len(tools)}."
    return "found", body, categories[:4] or ["toolbelt"]


def brain_provider_status() -> tuple[str, str, list[str]]:
    data = read_json(BRAIN_PROVIDER_REGISTRY)
    if not data:
        return "missing", "Registry de prioridade do cerebro nao encontrado.", ["brain"]
    order = data.get("routing_order") or data.get("priority_order") or []
    status = data.get("status") or data.get("registry_status") or "status desconhecido"
    body = f"{status}. Ordem declarada: {', '.join(order[:4]) if isinstance(order, list) and order else 'nao informada'}."
    return "found", body, ["free-first", "paid locked"]


def audit_status(path: Path) -> tuple[str, str, list[str]]:
    signal = markdown_signal(path, ("veredito", "classificacao", "resumo executivo", "falhas principais"))
    chips = ["auditoria", "sanitizada"] if signal["state"] == "found" else ["pendente"]
    return signal["state"], signal["signal"], chips


def main() -> None:
    inject_style()

    st.title("K-OS Cloud Status")
    st.markdown(
        """
        <section class="kos-banner">
          <div class="kos-title">Nucleo soberano permanece local</div>
          <div class="kos-text">
            Este runtime cloud e somente leitura, pensado para acompanhamento mobile 24/7.
            O operador completo, memoria sensivel, tokens e execucao real permanecem fora da nuvem.
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Blocos Principais")

    state, body, chips = gmail_status()
    card("Gmail real conectado", state, body, chips)

    state, body, chips = google_toolbelt_status()
    card("Google AI Toolbelt", state, body, chips)

    state, body, chips = brain_provider_status()
    card("Brain Provider Priority", state, body, chips)

    state, body, chips = audit_status(BROWSER_AUDIT)
    card("Browser Audit", state, body, chips)

    state, body, chips = audit_status(RENDER_AUDIT)
    card("Render Audit", state, body, chips)

    st.subheader("Proximos Passos")
    for item in ["Operator Intent Router", "Render deploy read-only", "Mobile Command Center"]:
        st.markdown(f"<div class='kos-card'><div class='kos-title'>{item}</div></div>", unsafe_allow_html=True)

    st.subheader("Guardrails")
    blocked_runtime = "local" + "_" + "runtime"
    guardrails = [
        "sem envio de email",
        "sem delete",
        "sem publish",
        "sem secrets",
        "sem Bau sensivel",
        f"sem {blocked_runtime}",
    ]
    st.markdown(
        "<div class='kos-chip-row'>" + "".join(f"<span class='kos-chip'>{item}</span>" for item in guardrails) + "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
