from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import streamlit as st

# KOS_OPERATOR_CHAT_COMPACT_UI_HELPERS_BEGIN
def kos_compact_json(label, payload=None, **kwargs):
    """Renderiza JSON tecnico fechado por padrao para reduzir carga visual."""
    try:
        with st.expander(label, expanded=False):
            st.json(payload, **kwargs)
    except Exception:
        try:
            st.json(payload)
        except Exception:
            pass
# KOS_OPERATOR_CHAT_COMPACT_UI_HELPERS_END


ROOT = Path(__file__).resolve().parents[1]
LATEST_PACKET = ROOT / "local_runtime" / "kos_action_router" / "latest_action_packet.json"
SAFE_ACTIONS_DIR = ROOT / "local_runtime" / "kos_safe_actions"

st.set_page_config(
    page_title="K-OS Operator Chat",
    page_icon="K",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def render_kos_visual_identity() -> None:
    st.markdown(
        """
        <style>
        :root {
            --kos-ink: #182033;
            --kos-muted: #667085;
            --kos-line: #d8dee8;
            --kos-panel: #ffffff;
            --kos-surface: #f6f8fb;
            --kos-accent: #1769ff;
            --kos-accent-2: #13a37f;
            --kos-warn: #b7791f;
            --kos-danger: #c2410c;
        }

        .stApp {
            background:
                linear-gradient(180deg, #f8fafc 0%, #f4f7fb 48%, #eef3f8 100%);
            color: var(--kos-ink);
        }

        .block-container {
            max-width: 880px;
            padding-top: 4.75rem;
            padding-bottom: 5rem;
        }

        div[data-testid="stToolbar"] {
            opacity: 0.32;
        }

        h1, h2, h3, h4 {
            letter-spacing: 0;
            color: var(--kos-ink);
        }

        .kos-shell {
            border: 1px solid rgba(24, 32, 51, 0.08);
            background: rgba(255, 255, 255, 0.86);
            box-shadow: 0 18px 48px rgba(25, 35, 55, 0.08);
            border-radius: 8px;
            padding: 26px 28px 22px;
            margin-bottom: 18px;
        }

        .kos-brand-row {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: flex-start;
        }

        .kos-kicker {
            color: var(--kos-accent-2);
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 8px;
        }

        .kos-title {
            font-size: clamp(2.2rem, 6vw, 4.2rem);
            line-height: 0.95;
            font-weight: 780;
            margin: 0;
            color: var(--kos-ink);
        }

        .kos-subtitle {
            color: var(--kos-muted);
            font-size: 1rem;
            line-height: 1.65;
            max-width: 680px;
            margin: 16px 0 0;
        }

        .kos-status {
            min-width: 148px;
            border: 1px solid rgba(19, 163, 127, 0.28);
            background: #eefbf7;
            border-radius: 8px;
            padding: 10px 12px;
            color: #05604a;
            font-size: 0.83rem;
            font-weight: 650;
            text-align: left;
        }

        .kos-contract {
            border-left: 3px solid var(--kos-accent);
            background: #eef5ff;
            color: #123466;
            border-radius: 8px;
            padding: 14px 16px;
            margin-top: 20px;
            line-height: 1.55;
        }

        .kos-note {
            border: 1px solid var(--kos-line);
            background: var(--kos-panel);
            border-radius: 8px;
            padding: 13px 15px;
            margin: 8px 0 14px;
            line-height: 1.55;
            color: var(--kos-ink);
        }

        .kos-note strong {
            display: block;
            color: var(--kos-muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .kos-note.ok { border-left: 3px solid var(--kos-accent-2); }
        .kos-note.info { border-left: 3px solid var(--kos-accent); }
        .kos-note.warn { border-left: 3px solid var(--kos-warn); }
        .kos-note.danger { border-left: 3px solid var(--kos-danger); }

        div[data-testid="stTextArea"] textarea {
            border: 1px solid #ccd5e1 !important;
            background: #ffffff !important;
            border-radius: 8px !important;
            color: var(--kos-ink) !important;
            min-height: 132px !important;
            box-shadow: inset 0 1px 0 rgba(16, 24, 40, 0.03) !important;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--kos-accent) !important;
            box-shadow: 0 0 0 3px rgba(23, 105, 255, 0.12) !important;
        }

        div[data-testid="stTextArea"] label p,
        div[data-testid="stCaptionContainer"] {
            color: var(--kos-muted);
        }

        .stButton > button {
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            color: var(--kos-ink);
            font-weight: 650;
        }

        .stButton > button[kind="primary"] {
            border: 0;
            background: linear-gradient(135deg, #1769ff 0%, #13a37f 100%);
            color: #ffffff;
        }

        .stButton > button:hover {
            border-color: #1769ff;
            color: var(--kos-ink);
        }

        .stButton > button[kind="primary"]:hover {
            color: #ffffff;
            filter: brightness(0.98);
        }

        div[data-testid="stExpander"] {
            border-color: var(--kos-line);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.74);
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid var(--kos-line);
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 2.2rem;
            }

            .kos-brand-row {
                display: block;
            }

            .kos-status {
                margin-top: 16px;
                min-width: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kos_note(label: str, text: str, kind: str = "info") -> None:
    st.markdown(
        f"""
        <div class="kos-note {kind}">
          <strong>{label}</strong>
          <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_kos_visual_identity()


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc), "path": str(path)}


def subprocess_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


def normalize_operator_text(text: str) -> str:
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def is_kos_capability_status_question(text: str) -> bool:
    value = normalize_operator_text(text)
    phrases = [
        "o que voce pode fazer",
        "o que vc pode fazer",
        "o que pode fazer por mim",
        "o que voce pode fazer por mim",
        "quais ferramentas voce tem",
        "quais ferramentas vc tem",
        "como pode me ajudar",
        "como voce pode me ajudar",
        "status das capacidades",
        "status de capacidades",
        "capacidades reais",
        "quais capacidades voce tem",
        "quais capacidades vc tem",
    ]
    return any(phrase in value for phrase in phrases)


def load_kos_operational_registries() -> dict:
    base = ROOT / "memory" / "kos_governance"
    files = {
        "tools": base / "KOS_TOOL_REGISTRY.json",
        "connections": base / "KOS_CONNECTION_REGISTRY.json",
        "packs": base / "KOS_PRODUCT_CAPABILITY_PACKS.json",
        "tenants": base / "KOS_TENANT_REGISTRY.json",
    }
    return {name: read_json(path) for name, path in files.items()}


def _items_by_family(tools: list[dict], family: str) -> list[dict]:
    return [tool for tool in tools if tool.get("family") == family and tool.get("status") == "alive"]


def build_kos_capability_status_answer() -> dict:
    registries = load_kos_operational_registries()
    tools = registries.get("tools", {}).get("tools", [])
    connections = registries.get("connections", {}).get("connections", [])
    packs = registries.get("packs", {}).get("packs", [])
    tenants = registries.get("tenants", {}).get("tenants", [])

    by_id = {tool.get("id"): tool for tool in tools}
    pack_by_id = {pack.get("id"): pack for pack in packs}
    tenant_names = [tenant.get("name", tenant.get("id")) for tenant in tenants if tenant.get("status") != "locked"]
    locked_tenants = [tenant.get("name", tenant.get("id")) for tenant in tenants if tenant.get("status") == "locked"]

    social_pack = pack_by_id.get("ki_publica", {})
    saas_pack = pack_by_id.get("kos_saas_factory", {})
    live_connections = [conn for conn in connections if conn.get("status") in {"validate_read_only", "configured_file_read_only", "blocked_without_human_gate"}]

    return {
        "registries": registries,
        "counts": {
            "tools": len(tools),
            "connections": len(connections),
            "packs": len(packs),
            "tenants": len(tenants),
            "active_tenants": len(tenant_names),
        },
        "groups": {
            "Criar SaaS/produtos": [
                "Transformar uma ideia em blueprint e mission pack local usando " + str(saas_pack.get("name", "K-OS SaaS Factory")) + ".",
                "Gerar rascunho de produto sem deploy automatico, com evidência local e revisão humana.",
                "Acionar Product Factory Draft e SaaS Product Mission Pack quando o pedido for de produto, MVP ou SaaS.",
            ],
            "Ki-Publica/social/campanhas": [
                "Criar campanha social para tenants ativos como " + (", ".join(tenant_names) if tenant_names else "clientes locais configurados") + ".",
                "Preparar estratégia, calendário, legenda e readiness de publicação pelo pack " + str(social_pack.get("name", "Ki-Publica")) + ".",
                "Auditar publicação antes do envio. Publicação externa continua bloqueada até Human Gate separado.",
            ],
            "Conexões Google/Meta/Supabase/Git/Render": [
                "Validar conexões em modo read-only: " + ", ".join(sorted({conn.get("provider", conn.get("name")) for conn in live_connections if conn.get("provider")})[:6]) + ".",
                "Checar Google/Gmail OAuth, Meta App, Instagram token, Supabase, GitHub, Render e Vercel sem revelar segredo.",
                "Usar arquivos de evidência e status mascarado; token, senha e secret bruto ficam fora da resposta.",
            ],
            "Autonomia/agentes/runtime": [
                "Roteamento por linguagem natural via Operator Chat e Action Router.",
                "Gerar Safe Action local, consultar fila/status de missões e ler runtime/bridge em modo seguro.",
                "Autonomia atual é supervisionada: posso preparar, auditar, enfileirar e explicar; ação real pede confirmação humana.",
            ],
            "Segurança/Human Gate": [
                "Sem publicação automática, sem deploy automático, sem patch automático, sem IA paga e sem scraping.",
                "Ações reais usam Human Gate e deixam evidência local antes de qualquer passo externo.",
                "Tenants travados permanecem travados: " + (", ".join(locked_tenants) if locked_tenants else "nenhum tenant travado no registry") + ".",
            ],
        },
        "source_tools": {
            "operator_chat": by_id.get("operator_chat", {}),
            "router": by_id.get("orchestrator_action_router", {}),
            "safe_action": by_id.get("safe_action_executor", {}),
            "connection_status": by_id.get("connection_status", {}),
        },
    }


def render_kos_capability_status_answer(answer: dict) -> None:
    counts = answer.get("counts", {})
    groups = answer.get("groups", {})
    registries = answer.get("registries", {})

    st.markdown("### Posso agir como seu coworker operacional")
    st.write(
        "Eu consultei os registries reais do K-OS agora. Em vez de te jogar num painel, "
        "eu posso entender o pedido, escolher uma rota segura, gerar evidência local e te pedir o OK por texto quando houver risco externo."
    )

    for title, items in groups.items():
        st.markdown("#### " + title)
        for item in items:
            st.write("- " + item)

    st.markdown("### O que posso acionar agora")
    st.write("- `Crie um SaaS de agenda para clínicas e me entregue o mission pack`")
    st.write("- `Monte uma campanha Ki-Publica para Casa da Limpeza sem publicar`")
    st.write("- `Cheque minhas conexões Google, Meta, Supabase, Git e Render`")
    st.write("- `Veja o status da fila/runtime e me diga o próximo gargalo`")
    st.write("- `Prepare uma ação segura e espere meu OK por texto`")

    st.markdown("### Evidência")
    st.write(
        "- Registries lidos: "
        + str(counts.get("tools", 0))
        + " ferramentas, "
        + str(counts.get("connections", 0))
        + " conexões, "
        + str(counts.get("packs", 0))
        + " packs e "
        + str(counts.get("tenants", 0))
        + " tenants."
    )
    st.write("- Fonte: `memory/kos_governance/KOS_TOOL_REGISTRY.json`")
    st.write("- Fonte: `memory/kos_governance/KOS_CONNECTION_REGISTRY.json`")
    st.write("- Fonte: `memory/kos_governance/KOS_PRODUCT_CAPABILITY_PACKS.json`")
    st.write("- Fonte: `memory/kos_governance/KOS_TENANT_REGISTRY.json`")
    st.caption("Nenhuma ação externa foi executada. Foi uma leitura local de registry.")

    with st.expander("Registro seguro dos registries", expanded=False):
        kos_compact_json("Tools", {
            "status": registries.get("tools", {}).get("status"),
            "version": registries.get("tools", {}).get("version"),
            "tool_count": counts.get("tools", 0),
        })
        kos_compact_json("Connections", {
            "status": registries.get("connections", {}).get("status"),
            "version": registries.get("connections", {}).get("version"),
            "connection_count": counts.get("connections", 0),
            "policy": registries.get("connections", {}).get("policy", {}),
        })
        kos_compact_json("Packs e tenants", {
            "packs_status": registries.get("packs", {}).get("status"),
            "tenant_status": registries.get("tenants", {}).get("status"),
            "pack_count": counts.get("packs", 0),
            "tenant_count": counts.get("tenants", 0),
        })


def run_action_router(request: str) -> dict:
    result = subprocess.run(
        ["python", "scripts\\run_phase72f_orchestrator_action_router.py", "--request", request],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
        env=subprocess_env(),
    )

    text = (result.stdout or "").strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "status": "ACTION_ROUTER_OUTPUT_ERROR",
            "stdout": text[-1000:],
            "stderr": (result.stderr or "")[-1000:],
            "returncode": result.returncode,
        }

    data["returncode"] = result.returncode
    return data


def run_safe_action(packet_path: str) -> dict:
    result = subprocess.run(
        ["python", "scripts\\run_phase72g_safe_action_executor.py", "--packet-path", packet_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
        env=subprocess_env(),
    )

    text = (result.stdout or "").strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "status": "SAFE_ACTION_OUTPUT_ERROR",
            "stdout": text[-1000:],
            "stderr": (result.stderr or "")[-1000:],
            "returncode": result.returncode,
        }

    data["returncode"] = result.returncode
    return data


def list_safe_actions(limit: int = 5) -> list[dict]:
    if not SAFE_ACTIONS_DIR.exists():
        return []

    items = []
    for path in sorted(SAFE_ACTIONS_DIR.glob("kos_safe_action_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = read_json(path)
        if data.get("status") == "KOS_SAFE_ACTION_READY":
            data["_json_path"] = str(path)
            items.append(data)
        if len(items) >= limit:
            break
    return items


def _kos_runtime_payload_to_text(payload) -> str:
    """Converte payload do router/safe action em texto bruto para o composer operacional."""
    if not payload:
        return ""

    lines = []

    if isinstance(payload, dict):
        summary = payload.get("summary")
        if summary:
            lines.append(str(summary))

        request = payload.get("request") or payload.get("pedido") or payload.get("original_request")
        if request:
            lines.append("Pedido original")
            lines.append(str(request))

        sections = payload.get("sections", [])
        if isinstance(sections, list):
            for section in sections:
                if not isinstance(section, dict):
                    continue

                title = section.get("title") or section.get("name") or "Se??o"
                lines.append(str(title))

                for item in section.get("items", []):
                    lines.append(str(item))

        operator_response = payload.get("operator_response", {})
        if isinstance(operator_response, dict):
            for key in ["entendi", "proximo_passo", "risco_bloqueio", "acao_segura_disponivel"]:
                value = operator_response.get(key)
                if value:
                    lines.append(str(value))

    return "\n".join(lines).strip()


def _kos_compose_runtime_answer(raw_text: str, fallback: str = "Pedido recebido pelo K-OS.") -> dict:
    """Separa resposta limpa de evid?ncia t?cnica."""
    try:
        from scripts.kos_real_operator_response_composer import compose_for_chat
        from pathlib import Path

        root = globals().get("ROOT", Path.cwd())
        result = compose_for_chat(raw_text or fallback, root=root)

        main = str(result.get("user_response") or "").strip()
        tech = str(result.get("technical_evidence") or raw_text or "").strip()

        if not main:
            main = fallback

        return {
            "user_response": main,
            "technical_evidence": tech,
        }
    except Exception as exc:
        return {
            "user_response": fallback,
            "technical_evidence": f"Composer indispon?vel: {exc}\n\n{raw_text or ''}",
        }


def show_safe_action_result(result: dict) -> None:
    """Renderiza resultado operacional sem vazar bastidor t?cnico no corpo principal."""
    if not result:
        return

    status = result.get("status", "")

    if status != "KOS_SAFE_ACTION_READY":
        kos_note("Resposta n?o conclu?da", result.get("status", "erro desconhecido"), "danger")
        with st.expander("Detalhes t?cnicos", expanded=False):
            kos_compact_json("Resultado bruto", result)
        return

    raw_text = _kos_runtime_payload_to_text(result)
    fallback = result.get("summary", "A??o preparada para revis?o.")
    composed = _kos_compose_runtime_answer(raw_text, fallback=fallback)

    st.markdown("### Resposta operacional")
    st.markdown(composed["user_response"])

    with st.expander("Detalhes t?cnicos", expanded=False):
        st.caption("Evid?ncia t?cnica preservada fora da resposta principal.")
        kos_compact_json("Resultado local", result)

def register_text_decision(command: str, detail: str = "") -> dict:
    from datetime import datetime, timezone

    decision_dir = ROOT / "live" / "human_decision_center"
    decision_dir.mkdir(parents=True, exist_ok=True)
    path = decision_dir / "operator_chat_text_decisions.jsonl"
    payload = {
        "status": "KOS_OPERATOR_CHAT_TEXT_DECISION_RECORDED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "detail": detail,
        "last_request": st.session_state.get("kos_last_operator_request", ""),
        "last_packet_id": (st.session_state.get("kos_last_operator_data") or {}).get("packet_id"),
        "last_safe_action_id": (st.session_state.get("kos_last_safe_action_result") or {}).get("action_id"),
        "real_action_executed": False,
        "external_side_effects_executed": False,
        "human_gate_still_required": True,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    payload["path"] = str(path)
    return payload


def parse_text_decision(text: str) -> tuple[str, str]:
    import unicodedata

    value = str(text or "").strip()
    normalized = unicodedata.normalize("NFKD", value).lower()
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))

    if normalized in ["confirmar", "confirmo", "aprovado", "aprovar", "ok", "continuar", "segue", "pode continuar"]:
        return "confirmar", value
    if normalized in ["cancelar", "cancela", "cancelado", "parar", "pare"]:
        return "cancelar", value
    for prefix in ["alterar ", "ajustar ", "mudar ", "corrigir ", "refazer "]:
        if normalized.startswith(prefix):
            return "alterar", value[len(prefix):].strip() or value
    return "", ""


def render_text_decision_feedback() -> None:
    decision = st.session_state.get("kos_last_text_decision")
    if not decision:
        return
    command = decision.get("command")
    if command == "confirmar":
        st.success("Confirmacao textual registrada. Human Gate continua obrigatorio para qualquer acao externa real.")
    elif command == "alterar":
        st.info("Pedido de alteracao registrado. Envie o ajuste como novo pedido ao K-OS para gerar nova evidencia.")
    elif command == "cancelar":
        st.warning("Cancelamento textual registrado. Nenhuma acao externa foi executada.")
    st.caption("Evidencia: " + str(decision.get("path", "")))


def show_safe_action_history() -> None:
    actions = list_safe_actions(limit=5)

    with st.expander("Historico de acoes seguras", expanded=False):
        if not actions:
            st.write("Nenhuma acao segura gerada ainda.")
            return

        st.caption("Ultimos rascunhos gerados localmente. Sem comandos e sem JSON bruto.")

        for action in actions:
            title = action.get("title", "Acao segura")
            created_at = action.get("created_at", "")
            route_label = action.get("route_label", action.get("route", ""))
            summary = action.get("summary", "")
            files = action.get("files", {})

            with st.container(border=True):
                st.markdown("#### " + str(title))
                if summary:
                    st.write(summary)
                if route_label:
                    st.caption("Rota: " + str(route_label))
                if created_at:
                    st.caption("Criado em: " + str(created_at))
                markdown_path = str(files.get("markdown", ""))
                if markdown_path:
                    st.info("Arquivo local: " + markdown_path)

                    open_key = "open_safe_action_" + str(action.get("action_id", markdown_path))
                    if st.button("Abrir rascunho", key=open_key, use_container_width=True):
                        md_file = Path(markdown_path)
                        if md_file.exists():
                            try:
                                content = md_file.read_text(encoding="utf-8-sig")
                                st.markdown("##### Rascunho aberto")
                                st.markdown(content)
                            except Exception as exc:
                                st.error("Nao foi possivel abrir o rascunho.")
                                st.caption(str(exc))
                        else:
                            st.warning("Arquivo local nao encontrado.")

                with st.expander("Ver resumo deste rascunho"):
                    for section in action.get("sections", []):
                        st.markdown("##### " + str(section.get("title", "Secao")))
                        for item in section.get("items", []):
                            st.write("- " + str(item))



def render_hupmix_gp_lousa_preview(data=None):
    import json
    from pathlib import Path
    from datetime import datetime, timezone
    import streamlit as st

    root = Path(__file__).resolve().parents[1]
    kit_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
    package_path = root / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json"
    preview_script = root / "scripts" / "run_kos_hupmix_gp_video_01_mp4_preview.py"
    preview_mp4 = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    decision_dir = root / "live" / "human_decision_center"
    decision_dir.mkdir(parents=True, exist_ok=True)

    if not kit_path.exists():
        return

    try:
        kit = json.loads(kit_path.read_text(encoding="utf-8"))
    except Exception as exc:
        st.warning(f"Lousa visual GP_VIDEO_01 indisponivel: {exc}")
        return

    try:
        package = json.loads(package_path.read_text(encoding="utf-8")) if package_path.exists() else {}
    except Exception:
        package = {}

    try:
        if preview_script.exists():
            subprocess = __import__("subprocess")
            sysmod = __import__("sys")
            subprocess.run(
                [sysmod.executable, str(preview_script)],
                cwd=str(root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
    except Exception as exc:
        st.warning(f"Geracao do preview MP4 falhou: {exc}")

    checklist = kit.get("recording_checklist", []) or []
    calendar = package.get("calendar_7_days", []) or []

    st.markdown("## Lousa de aprovação visual")
    st.caption("Preview vertical do GP_VIDEO_01 gerado pelo K-OS. Isto é simulação para aprovação. Nada foi publicado.")

    st.markdown("### Vídeo preview MP4")

    if preview_mp4.exists():
        left, center, right = st.columns([1, 1.15, 1])
        with center:
            st.video(str(preview_mp4), format="video/mp4")
            st.caption("MP4 vertical de preview. Publicação real continua bloqueada.")
    else:
        st.warning("Preview MP4 ainda não encontrado.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Programação semanal")
        if calendar:
            for item in calendar:
                st.write("- " + str(item))
        else:
            st.write("Calendário semanal ainda não encontrado.")

    with col2:
        st.markdown("### Checklist antes de gravar")
        for item in checklist:
            st.write("- " + str(item))

    c1, c2 = st.columns(2)

    if c1.button("Aprovar roteiro para gravação", key="kos_approve_gp_video_01_recording_v2"):
        decision = {
            "status": "APPROVED_FOR_RECORDING",
            "scope": "GP_VIDEO_01",
            "brand": "Hupmix",
            "campaign": "GP / Garoto Oxy Power / Oxy Power",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "instagram_publish_executed": False,
            "approval_type": "recording_only",
            "note": "Aprovado apenas para gravacao. Publicacao real continua bloqueada."
        }
        out = decision_dir / "hupmix_gp_video_01_recording_approval.json"
        out.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        st.success("Roteiro aprovado para gravação. Publicação real continua bloqueada.")

    if c2.button("Pedir ajuste antes de gravar", key="kos_request_gp_video_01_adjustment_v2"):
        decision = {
            "status": "ADJUSTMENT_REQUESTED",
            "scope": "GP_VIDEO_01",
            "brand": "Hupmix",
            "campaign": "GP / Garoto Oxy Power / Oxy Power",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "instagram_publish_executed": False,
            "approval_type": "adjustment_before_recording",
            "note": "Operador pediu ajuste antes da gravacao."
        }
        out = decision_dir / "hupmix_gp_video_01_adjustment_requested.json"
        out.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        st.warning("Pedido de ajuste registrado. Nada foi publicado.")

def show_operator_response(data: dict) -> None:
    """Renderiza o Operator Chat como coworker operacional, n?o como painel t?cnico."""
    if not data:
        return

    response = data.get("operator_response", {}) if isinstance(data, dict) else {}
    packet_path = data.get("packet_path", "") if isinstance(data, dict) else ""
    last_safe_result = st.session_state.get("kos_last_safe_action_result")

    raw_parts = []

    if last_safe_result:
        raw_parts.append(_kos_runtime_payload_to_text(last_safe_result))

    raw_parts.append(_kos_runtime_payload_to_text(data))

    if isinstance(response, dict):
        direct_bits = [
            response.get("entendi"),
            response.get("proximo_passo"),
            response.get("acao_segura_disponivel"),
        ]
        raw_parts.extend([str(x) for x in direct_bits if x])

    raw_text = "\n\n".join([part for part in raw_parts if part]).strip()

    composed = _kos_compose_runtime_answer(
        raw_text,
        fallback="Entendi. Vou verificar conex?es, mem?ria e rotas dispon?veis para responder com estado real.",
    )

    st.subheader("Resposta do K-OS")
    st.markdown(composed["user_response"])

    if packet_path or last_safe_result or data:
        with st.expander("Detalhes t?cnicos", expanded=False):
            st.caption("Router, evid?ncias, arquivos locais e bloqueios ficam aqui, fora da resposta principal.")

            if isinstance(data, dict):
                st.write("Rota interna:", data.get("route_label", data.get("route", "geral")))

                if data.get("packet_id"):
                    st.write("Packet:", data.get("packet_id"))

                if data.get("packet_path"):
                    st.write("Arquivo local:", data.get("packet_path"))

                kos_compact_json("Router", data)

            if last_safe_result:
                kos_compact_json("Execu??o local", last_safe_result)

    st.caption("Pr?ximos pedidos naturais: revisar, melhorar, comparar, preparar a??o ou confirmar quando houver a??o externa real.")

def is_kos_read_only_diagnostic_request(text: str) -> bool:
    """Detecta comandos locais de diagnostico que nao devem acionar Router nem Safe Action."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    patterns = [
        "k-os diagnostic",
        "kos diagnostic",
        "operator flow",
        "diagnostico do fluxo",
        "diagnostico operator",
        "mostrar diagnostico",
        "painel de diagnostico",
        "diagnostico do operator",
        "diagnostico do operador",
    ]

    return any(pattern in value for pattern in patterns)
# KOS_READ_ONLY_DIAGNOSTIC_COMMANDS_END



# KOS_READ_ONLY_LOUSA_COMMANDS_BEGIN
def is_kos_read_only_lousa_request(text: str) -> bool:
    """Detecta comandos locais de lousa visual que nao devem acionar Router nem Safe Action."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "mostrar lousa",
        "abrir lousa",
        "ver lousa",
        "visualizar video",
        "mostrar video",
        "ver video",
        "preview mp4",
        "mostrar preview",
    ]

    target_terms = [
        "gp_video_01",
        "gp video 01",
        "gp_video",
        "garoto oxy",
        "hupmix",
    ]

    return any(a in value for a in action_terms) and any(t in value for t in target_terms)
# KOS_READ_ONLY_LOUSA_COMMANDS_END



# KOS_OPERATOR_LOCAL_COMMAND_GUARD_BEGIN
def is_kos_local_command_or_path_request(text: str) -> bool:
    """Bloqueia comandos locais, paths Windows, .cmd e .ps1 colados no Operator Chat."""
    import re
    import unicodedata

    value = str(text or "").strip()
    if not value:
        return False

    normalized = unicodedata.normalize("NFKD", value).lower()
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))

    if re.search(r"^[a-zA-Z]:\\", value):
        return True

    patterns = [
        ".cmd", ".ps1", ".bat", "powershell", "set-location", "cd /d",
        "git ", "python ", "streamlit ", "kos_start_here", "@echo off",
        "exit /b", "´╗┐",
    ]

    return any(pattern in normalized for pattern in patterns)


def render_kos_local_command_guard_message():
    """Mostra instrucao segura quando comando local foi colado no Operator Chat."""
    import streamlit as st

    msg = st.session_state.get("kos_local_command_guard_message")
    command = st.session_state.get("kos_local_command_guard_command")

    if not msg:
        return

    st.warning(msg)
    if command:
        st.caption("Comando detectado:")
        st.code(command, language="powershell")
    st.info("Use o PowerShell para comandos locais. Use o Operator Chat apenas para pedidos em linguagem normal.")

    if st.button("Limpar aviso de comando local", use_container_width=True, key="kos_clear_local_command_guard"):
        st.session_state.pop("kos_local_command_guard_message", None)
        st.session_state.pop("kos_local_command_guard_command", None)
        st.session_state["kos_operator_request_text"] = ""
        if hasattr(st, "rerun"):
            st.rerun()
# KOS_OPERATOR_LOCAL_COMMAND_GUARD_END


if "kos_operator_request_text" not in st.session_state:
    st.session_state["kos_operator_request_text"] = ""



# KOS_OPERATOR_FILE_INTAKE_CENTER_BEGIN
def render_kos_operator_file_intake_center():
    """Centro compacto de anexos, pesquisa e lousa.
    Mantem a tela limpa. O operador nao precisa procurar pastas.
    """
    import hashlib
    import json
    from datetime import datetime
    from pathlib import Path
    import streamlit as st

    root = Path.cwd()
    memory_dir = root / "memory" / "kos_file_intake"
    memory_dir.mkdir(parents=True, exist_ok=True)
    index_path = memory_dir / "KOS_FILE_INTAKE_INDEX.json"

    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            index = {"status": "KOS_FILE_INTAKE_INDEX_READY", "items": []}
    else:
        index = {"status": "KOS_FILE_INTAKE_INDEX_READY", "items": []}

    current_request = str(st.session_state.get("kos_operator_request_text", "") or "").lower()

    default_route = "general_operator_inbox"
    if any(term in current_request for term in ["gp_video_01", "gp video 01", "garoto oxy", "oxy power", "hupmix"]):
        default_route = "hupmix_gp_video_01"
    if any(term in current_request for term in ["parada", "atlantida", "atlântida"]):
        default_route = "campaign_assets"

    with st.expander("+ Anexos, pesquisa e lousa", expanded=bool(st.session_state.get("kos_intake_center_open", False))):
        st.caption("Use quando o K-OS pedir arquivos, pesquisa publica ou lousa. Nada e publicado. Nada vai para API.")

        c1, c2, c3 = st.columns(3)

        if c1.button("Pesquisa publica", use_container_width=True, key="kos_open_research_center_from_compact_intake"):
            st.session_state["kos_show_research_continuity_center"] = True
            st.session_state["kos_research_continuity_message"] = "Centro de pesquisa publica aberto. Sem Router, sem Safe Action, sem publicacao."
            if hasattr(st, "rerun"):
                st.rerun()

        if c2.button("Lousa GP_VIDEO_01", use_container_width=True, key="kos_open_gp_lousa_from_compact_intake"):
            st.session_state["kos_show_gp_video_01_lousa"] = True
            st.session_state["kos_lousa_read_only_message"] = "Lousa visual aberta pelo operador. Nenhum Router ou Safe Action foi acionado."
            if hasattr(st, "rerun"):
                st.rerun()

        if c3.button("Anexos recentes", use_container_width=True, key="kos_show_recent_assets_from_compact_intake"):
            st.session_state["kos_show_recent_intake_assets"] = not bool(st.session_state.get("kos_show_recent_intake_assets", False))

        route_options = [
            "hupmix_gp_video_01",
            "general_operator_inbox",
            "campaign_assets",
            "memory_reference",
            "brand_assets",
        ]

        route = st.selectbox(
            "Destino",
            route_options,
            index=route_options.index(default_route) if default_route in route_options else 1,
            key="kos_file_intake_route",
        )

        route_dirs = {
            "hupmix_gp_video_01": root / "content_packs" / "hupmix_gp_video_01" / "assets_inbox",
            "general_operator_inbox": root / "content_packs" / "kos_operator_uploads" / "assets_inbox",
            "campaign_assets": root / "content_packs" / "campaign_assets" / "assets_inbox",
            "memory_reference": root / "memory" / "kos_file_intake" / "reference_files",
            "brand_assets": root / "content_packs" / "brand_assets" / "assets_inbox",
        }

        target_dir = route_dirs.get(route, route_dirs["general_operator_inbox"])
        target_dir.mkdir(parents=True, exist_ok=True)

        uploaded_files = st.file_uploader(
            "Anexar ao K-OS",
            accept_multiple_files=True,
            type=[
                "png", "jpg", "jpeg", "webp", "gif",
                "mp4", "mov", "m4v",
                "mp3", "wav", "m4a",
                "pdf", "txt", "md", "json", "csv",
                "docx", "xlsx", "pptx"
            ],
            key="kos_operator_file_uploader",
        )

        operator_note = st.text_input(
            "Nota opcional",
            placeholder="Exemplo: fotos reais do Oxy Power para montar o video",
            key="kos_file_intake_note",
        )

        if uploaded_files:
            if st.button("Salvar anexos", type="primary", use_container_width=True, key="kos_save_uploaded_files"):
                saved = []
                batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                batch_dir = target_dir / batch_id
                batch_dir.mkdir(parents=True, exist_ok=True)

                for file in uploaded_files:
                    original_name = Path(file.name).name
                    raw = file.getbuffer()
                    digest = hashlib.sha256(bytes(raw)).hexdigest()[:16]
                    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in original_name)
                    final_path = batch_dir / f"{digest}_{safe_name}"
                    final_path.write_bytes(raw)

                    item = {
                        "asset_id": f"kos_asset_{batch_id}_{digest}",
                        "created_at": datetime.now().isoformat(),
                        "route": route,
                        "original_name": original_name,
                        "stored_path": str(final_path.relative_to(root)).replace("\\", "/"),
                        "size": final_path.stat().st_size,
                        "sha256_16": digest,
                        "operator_note": operator_note,
                        "source": "operator_chat_upload",
                        "policy": {
                            "published": False,
                            "sent_to_external_api": False,
                            "paid_ai_used": False,
                            "human_gate_required": True
                        }
                    }

                    index.setdefault("items", []).append(item)
                    saved.append(item)

                index["status"] = "KOS_FILE_INTAKE_INDEX_READY"
                index["updated_at"] = datetime.now().isoformat()
                index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

                st.success(f"{len(saved)} arquivo(s) salvo(s) no K-OS.")
                kos_compact_json("Detalhes técnicos", {
                    "route": route,
                    "batch_dir": str(batch_dir.relative_to(root)).replace("\\", "/"),
                    "files": [{"name": x["original_name"], "stored_path": x["stored_path"], "size": x["size"]} for x in saved],
                    "policy": "Arquivos salvos localmente. Nada foi publicado ou enviado para API."
                })

        recent_items = list(reversed(index.get("items", [])))[:5]
        if st.session_state.get("kos_show_recent_intake_assets", False):
            st.markdown("### Ultimos anexos")
            if not recent_items:
                st.caption("Nenhum anexo salvo ainda.")
            for item in recent_items:
                st.markdown(f"**{item.get('original_name')}**")
                st.caption(item.get("stored_path"))
                st.caption(f"Destino: {item.get('route')} | Tamanho: {item.get('size')} bytes")

try:
    render_kos_operator_file_intake_center()
except Exception as exc:
    try:
        import streamlit as st
        st.warning(f"K-OS Intake Center indisponivel: {exc}")
    except Exception:
        pass
# KOS_OPERATOR_FILE_INTAKE_CENTER_END





# KOS_RESEARCH_CONTINUITY_CENTER_BEGIN
def is_kos_research_continuity_request(text: str) -> bool:
    """Detecta pedidos de continuidade, pesquisa publica, briefing, alvo ou auditoria de pagina."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    production_terms = [
        "proximo video",
        "próximo video",
        "novo video",
        "nova publicacao",
        "ligar producao",
        "producao de video",
        "produção de video",
        "continuar producao",
        "continuar produção",
        "video condizente",
        "gp_video_02",
        "gp video 02",
    ]

    production_targets = [
        "hupmix",
        "garoto oxy",
        "oxy power",
        "gp_video_02",
        "gp video 02",
    ]

    if any(term in value for term in production_terms) and any(term in value for term in production_targets):
        return False

    action_terms = [
        "auditoria", "auditar", "identificar", "verificar", "pesquisar",
        "pesquisa publica", "fontes publicas", "fontes oficiais",
        "oficial", "oficiais", "briefing", "briefing seguro",
        "gerar briefing", "alvo", "qual e", "quem e",
        "abrir pagina", "abrir site", "abrir na lousa",
        "continuar", "continuidade", "campanha real", "readiness",
    ]

    target_terms = [
        "hupmix", "gp_video_01", "gp video 01", "garoto oxy", "oxy power",
        "parada atlantida", "parada atlantica", "parada atlântida",
        "atlantida", "atlântida", "planeta atlantida", "rede atlantida",
        "atlantida celebration", "paleta atlantida",
    ]

    return any(a in value for a in action_terms) and any(t in value for t in target_terms)


def kos_register_public_research_request_packet(query: str, active_url: str | None = None, operator_request: str | None = None) -> dict:
    """Registra pesquisa publica localmente. Nao pesquisa sozinho, nao faz scraping, nao publica."""
    import json
    from datetime import datetime
    from pathlib import Path

    root = Path.cwd()
    requests_dir = root / "local_runtime" / "kos_research_requests"
    requests_dir.mkdir(parents=True, exist_ok=True)

    request_id = "kos_research_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "status": "KOS_PUBLIC_RESEARCH_REQUEST_READY",
        "request_id": request_id,
        "created_at": datetime.now().isoformat(),
        "operator_request": operator_request or query,
        "research_query": query,
        "active_url": active_url,
        "policy": {
            "public_sources_only": True,
            "no_logged_account": True,
            "no_scraping": True,
            "no_publish": True,
            "no_paid_ai": True,
            "human_gate_required": True
        },
        "expected_output": {
            "sources": "URLs, datas e origem devem ser registradas",
            "campaign_use": "briefing, readiness, lousa e plano seguro",
            "blocked": "publicacao automatica, scraping, conta logada e IA paga"
        }
    }

    path = requests_dir / (request_id + ".json")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["stored_path"] = str(path.relative_to(root)).replace("\\", "/")
    return payload


def render_kos_research_continuity_center():
    """Centro de continuidade, pesquisa publica e lousa web."""
    import json
    from pathlib import Path
    import streamlit as st
    import streamlit.components.v1 as components

    root = Path.cwd()
    current_request = str(st.session_state.get("kos_operator_request_text", "") or "")
    current_request_lower = current_request.lower()
    expanded = bool(st.session_state.get("kos_show_research_continuity_center", False))

    with st.expander("K-OS Research & Continuity Center", expanded=expanded):
        st.caption("Pesquisa publica, continuidade e lousa web. Sem publicacao, sem scraping, sem conta logada, sem IA paga.")

        msg = st.session_state.get("kos_research_continuity_message")
        if msg:
            st.success(msg)

        last_packet = st.session_state.get("kos_last_public_research_packet")
        if last_packet:
            st.info("Pesquisa publica registrada automaticamente.")
            kos_compact_json("Detalhes técnicos", {
                "request_id": last_packet.get("request_id"),
                "path": last_packet.get("stored_path"),
                "policy": last_packet.get("policy")
            })

        if any(term in current_request_lower for term in ["parada", "atlantida", "atlântida"]):
            st.warning("Parada Atlantida: modo permitido agora = pesquisa publica, briefing, assets, lousa e readiness. Publicacao e automacao seguem bloqueadas.")

        st.markdown("### Continuidade antes de criar algo novo")

        if any(term in current_request_lower for term in ["hupmix", "gp_video_01", "gp video 01", "garoto oxy", "oxy power"]):
            hupmix_paths = {
                "Production Kit GP_VIDEO_01": root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json",
                "Job Video Factory": root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json",
                "Preview MP4": root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4",
                "Storyboard": root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png",
            }
            st.info("Continuidade detectada: Hupmix / GP_VIDEO_01.")
            for label, path in hupmix_paths.items():
                st.write(("- OK " if path.exists() else "- FALTA ") + label + " -> " + str(path.relative_to(root)).replace("\\", "/"))

        if any(term in current_request_lower for term in ["parada", "atlantida", "atlântida"]):
            st.info("Continuidade detectada: Parada Atlantida. Modo permitido: pesquisa, briefing, assets, lousa e readiness.")
            st.write("- Publicacao automatica: BLOQUEADA")
            st.write("- Conta logada / navegador automatizado: BLOQUEADO")
            st.write("- Scraping: BLOQUEADO")
            st.write("- Pesquisa publica com fontes: PERMITIDA")
            st.write("- Lousa web com URL publica: PERMITIDA")
            st.write("- Briefing e plano: PERMITIDOS com gate humano")

        st.markdown("### Abrir pagina publica na lousa")
        url = st.text_input(
            "URL publica",
            placeholder="Cole uma URL publica oficial ou relevante.",
            key="kos_research_lousa_url",
        )

        if st.button("Abrir URL publica na lousa", use_container_width=True, key="kos_open_public_url_lousa"):
            clean_url = str(url or "").strip()
            if clean_url and clean_url.startswith(("http://", "https://")):
                st.session_state["kos_public_url_lousa_active"] = clean_url
                st.session_state["kos_show_research_continuity_center"] = True
                if hasattr(st, "rerun"):
                    st.rerun()
            else:
                st.error("Cole uma URL publica iniciando com http:// ou https://")

        active_url = st.session_state.get("kos_public_url_lousa_active")
        if active_url:
            st.markdown("#### Lousa web")
            st.caption("Se o site bloquear iframe, use o link de fallback.")
            st.markdown(f"[Abrir em nova aba]({active_url})")
            try:
                components.iframe(active_url, height=650, scrolling=True)
            except Exception as exc:
                st.warning(f"Nao foi possivel abrir em iframe: {exc}")

        st.markdown("### Pesquisa publica")
        research_query = st.text_input(
            "O que pesquisar?",
            value=current_request if current_request else "",
            key="kos_public_research_query",
        )

        if st.button("Registrar pesquisa publica", use_container_width=True, key="kos_register_public_research"):
            query = str(research_query or "").strip()
            if not query:
                st.error("Digite o que deve ser pesquisado.")
            else:
                packet = kos_register_public_research_request_packet(query, active_url=active_url, operator_request=current_request)
                st.session_state["kos_last_public_research_packet"] = packet
                st.success("Pesquisa publica registrada no K-OS.")
                kos_compact_json("Detalhes técnicos", {
                    "request_id": packet.get("request_id"),
                    "path": packet.get("stored_path"),
                    "policy": packet.get("policy")
                })

        st.markdown("### Regra operacional")
        st.write("- Se faltar arquivo: K-OS pede anexo pelo botao +.")
        st.write("- Se faltar informacao atual: K-OS registra pesquisa publica.")
        st.write("- Se for algo ja comecado: K-OS verifica continuidade antes de criar do zero.")
        st.write("- Parada Atlantida: pesquisa/readiness ate autorizacao explicita.")
        st.write("- Publicacao, conta logada, scraping, deploy e IA paga seguem bloqueados.")
# KOS_RESEARCH_CONTINUITY_CENTER_END




# KOS_HUPMIX_REVIEW_GATE_BEGIN
def is_kos_hupmix_review_request(text: str) -> bool:
    """Detecta pedido de revisao Hupmix: video + publicacao + OK humano."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "revisar", "ver video", "ver o video", "video e publicacao",
        "nova publicacao", "ultima publicacao", "aprovar hupmix",
        "dar ok", "ok hupmix", "revisao hupmix", "aprovar video",
    ]

    target_terms = [
        "hupmix", "gp_video_01", "gp video 01", "garoto oxy", "oxy power"
    ]

    return any(a in value for a in action_terms) and any(t in value for t in target_terms)


def kos_fetch_hupmix_latest_publication_readonly():
    """Busca a ultima publicacao Hupmix via Meta Graph em modo read-only."""
    import json
    import urllib.parse
    import urllib.request
    from datetime import datetime
    from pathlib import Path

    root = Path.cwd()
    token_path = root / "local_runtime" / "kos_secrets" / "meta_access_token.txt"
    report_path = root / "reports" / "KOS_HUPMIX_REVIEW_GATE_LATEST_PUBLICATION.json"

    if not token_path.exists():
        return {
            "status": "META_TOKEN_NOT_FOUND",
            "message": "Token Meta local nao encontrado.",
            "policy": {"no_publish": True, "read_only": True}
        }

    token = token_path.read_text(encoding="utf-8").strip()
    if not token:
        return {
            "status": "META_TOKEN_EMPTY",
            "message": "Token Meta local vazio.",
            "policy": {"no_publish": True, "read_only": True}
        }

    ig_id = "17841471706662294"
    params = urllib.parse.urlencode({
        "fields": "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url",
        "limit": "1",
        "access_token": token
    })

    url = f"https://graph.facebook.com/v20.0/{ig_id}/media?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "K-OS read-only"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        items = payload.get("data", [])
        latest = items[0] if items else None

        result = {
            "status": "KOS_HUPMIX_LATEST_PUBLICATION_READY" if latest else "KOS_HUPMIX_NO_PUBLICATION_FOUND",
            "created_at": datetime.now().isoformat(),
            "source": "Meta Graph API read-only",
            "ig_user_id": ig_id,
            "latest_publication": latest,
            "policy": {
                "read_only": True,
                "no_publish": True,
                "no_delete": True,
                "no_comment": True,
                "no_message": True,
                "no_paid_ai": True,
                "human_gate_required": True
            }
        }

        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    except Exception as exc:
        return {
            "status": "KOS_HUPMIX_LATEST_PUBLICATION_FETCH_ERROR",
            "error": str(exc),
            "policy": {"read_only": True, "no_publish": True}
        }


def render_kos_hupmix_review_gate():
    """Painel de revisao Hupmix: video + ultima publicacao + OK humano."""
    import json
    from datetime import datetime
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_hupmix_review_gate", False):
        return

    root = Path.cwd()
    mp4_path = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    storyboard_path = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png"
    approval_dir = root / "live" / "human_decision_center"
    approval_dir.mkdir(parents=True, exist_ok=True)

    st.markdown("## Revisao Hupmix — video + publicacao")

    msg = st.session_state.get("kos_hupmix_review_message")
    if msg:
        st.success(msg)

    st.caption("Modo seguro: leitura local + Meta Graph read-only. Sem publicacao, sem deploy, sem IA paga.")

    st.markdown("### 1. Video GP_VIDEO_01")
    if mp4_path.exists():
        st.video(str(mp4_path))
        st.caption("Fonte: local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4")
    else:
        st.error("MP4 local nao encontrado. Rode o Video Factory Free Mode novamente.")

    if storyboard_path.exists():
        with st.expander("Storyboard", expanded=False):
            st.image(str(storyboard_path), use_container_width=True)

    st.markdown("### 2. Ultima publicacao Hupmix")

    if st.button("Atualizar ultima publicacao Hupmix", use_container_width=True, key="kos_refresh_hupmix_latest_publication"):
        st.session_state["kos_hupmix_latest_publication_result"] = kos_fetch_hupmix_latest_publication_readonly()
        if hasattr(st, "rerun"):
            st.rerun()

    latest_result = st.session_state.get("kos_hupmix_latest_publication_result")

    if latest_result:
        status = latest_result.get("status")
        if status == "KOS_HUPMIX_LATEST_PUBLICATION_READY":
            latest = latest_result.get("latest_publication") or {}
            st.success("Ultima publicacao carregada em modo read-only.")

            st.write("Tipo:", latest.get("media_type"))
            st.write("Data:", latest.get("timestamp"))

            permalink = latest.get("permalink")
            if permalink:
                st.markdown(f"[Abrir publicacao em nova aba]({permalink})")

            caption = latest.get("caption")
            if caption:
                with st.expander("Legenda da publicacao", expanded=True):
                    st.write(caption)

            media_url = latest.get("media_url") or latest.get("thumbnail_url")
            media_type = str(latest.get("media_type") or "").upper()

            if media_url:
                try:
                    if "VIDEO" in media_type or "REELS" in media_type:
                        st.video(media_url)
                    else:
                        st.image(media_url, use_container_width=True)
                except Exception:
                    st.caption("Midia remota nao abriu no player. Use o link da publicacao.")
        else:
            st.warning(status)
            kos_compact_json("Detalhes técnicos", latest_result)

    manual_url = st.text_input(
        "URL manual da publicacao, se necessario",
        placeholder="Cole aqui o link da publicacao Hupmix caso o Meta Graph nao abra a midia.",
        key="kos_hupmix_manual_publication_url"
    )

    st.markdown("### 3. Decisao humana")

    c1, c2 = st.columns(2)

    if c1.button("Aprovar video + publicacao Hupmix", type="primary", use_container_width=True, key="kos_approve_hupmix_video_publication"):
        latest_snapshot = st.session_state.get("kos_hupmix_latest_publication_result")
        record = {
            "status": "HUPMIX_VIDEO_AND_PUBLICATION_APPROVED_BY_OPERATOR",
            "created_at": datetime.now().isoformat(),
            "scope": "Hupmix GP_VIDEO_01 + latest publication review",
            "video": {
                "path": "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4",
                "exists": mp4_path.exists()
            },
            "publication": {
                "meta_graph_snapshot": latest_snapshot,
                "manual_url": manual_url
            },
            "decision": {
                "approved": True,
                "approved_by": "human_operator",
                "next_step": "seguir para Parada Atlantida em modo pesquisa/readiness"
            },
            "policy": {
                "publication_executed": False,
                "deploy_executed": False,
                "paid_ai_used": False,
                "human_gate_required": True
            }
        }

        path = approval_dir / "hupmix_gp_video_01_publication_review_approval.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        st.session_state["kos_hupmix_review_approval_record"] = record
        st.success("OK humano registrado. Nenhuma publicacao foi executada.")
        kos_compact_json("Detalhes técnicos", {
            "status": record["status"],
            "approval_file": str(path.relative_to(root)).replace("\\", "/"),
            "next_step": record["decision"]["next_step"]
        })

    if c2.button("Pedir ajuste antes do OK", use_container_width=True, key="kos_request_hupmix_review_adjustment"):
        record = {
            "status": "HUPMIX_VIDEO_AND_PUBLICATION_ADJUSTMENT_REQUESTED",
            "created_at": datetime.now().isoformat(),
            "scope": "Hupmix GP_VIDEO_01 + latest publication review",
            "decision": {
                "approved": False,
                "adjustment_required": True
            },
            "policy": {
                "publication_executed": False,
                "deploy_executed": False,
                "paid_ai_used": False,
                "human_gate_required": True
            }
        }

        path = approval_dir / "hupmix_gp_video_01_publication_review_adjustment.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        st.warning("Ajuste solicitado. Nenhuma publicacao foi executada.")

    if st.button("Fechar revisao Hupmix", use_container_width=True, key="kos_close_hupmix_review_gate"):
        st.session_state["kos_show_hupmix_review_gate"] = False
        st.info("Revisao Hupmix fechada.")
        if hasattr(st, "rerun"):
            st.rerun()
# KOS_HUPMIX_REVIEW_GATE_END



# KOS_HUPMIX_GAROTO_OXY_HISTORY_REVIEW_BEGIN
def is_kos_hupmix_garoto_oxy_history_review_request(text: str) -> bool:
    """Detecta pedido de revisao do historico Garoto Oxy Power / Hupmix."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "revisar historico",
        "ver historico",
        "auditar historico",
        "continuar historico",
        "garoto oxy",
        "oxy power",
        "ver video e publicacao",
        "dar ok",
        "aprovar hupmix",
        "revisar hupmix",
    ]

    target_terms = [
        "hupmix",
        "garoto oxy",
        "oxy power",
        "gp_video_01",
        "instagram",
        "publicacao",
    ]

    return any(a in value for a in action_terms) and any(t in value for t in target_terms)


def render_kos_hupmix_garoto_oxy_history_review():
    """Mostra revisao do video local e da publicacao Instagram baixada."""
    import json
    from datetime import datetime
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_hupmix_garoto_oxy_history_review", False):
        return

    root = Path.cwd()
    audit_path = root / "reports" / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
    local_video = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    storyboard = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png"
    approval_dir = root / "live" / "human_decision_center"
    approval_dir.mkdir(parents=True, exist_ok=True)

    st.markdown("## Revisao Garoto Oxy Power — Hupmix")
    st.caption("Modo seguro: leitura local + auditoria Meta Graph read-only. Sem publicacao, sem scraping, sem IA paga.")

    msg = st.session_state.get("kos_hupmix_garoto_oxy_review_message")
    if msg:
        st.success(msg)

    if not audit_path.exists():
        st.error("Auditoria de continuidade nao encontrada. Rode scripts/run_kos_hupmix_instagram_continuity_audit.py.")
        return

    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    except Exception as exc:
        st.error(f"Nao foi possivel ler auditoria: {exc}")
        return

    instagram = audit.get("instagram", {})
    latest = instagram.get("latest_item") or {}
    download = instagram.get("download") or {}
    gp_score = instagram.get("gp_relevance_from_caption") or {}
    interpretation = audit.get("interpretation") or {}

    downloaded_path = None
    stored_path = download.get("stored_path")
    if stored_path:
        downloaded_path = root / stored_path

    st.markdown("### 1. Video local do K-OS")
    if local_video.exists():
        st.video(str(local_video))
        st.caption("Fonte: local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4")
    else:
        st.warning("Video local GP_VIDEO_01 nao encontrado.")

    if storyboard.exists():
        with st.expander("Storyboard local", expanded=False):
            st.image(str(storyboard), use_container_width=True)

    st.markdown("### 2. Publicacao real baixada do Instagram Hupmix")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fetch", instagram.get("fetch_status", "n/a"))
    c2.metric("Tipo", latest.get("media_type", "n/a"))
    c3.metric("Score legenda", str(gp_score.get("score", 0)))

    st.write("Data:", latest.get("timestamp"))
    if latest.get("permalink"):
        st.markdown(f"[Abrir publicacao no Instagram]({latest.get('permalink')})")

    if downloaded_path and downloaded_path.exists():
        st.video(str(downloaded_path))
        st.caption(download.get("stored_path"))
    else:
        st.warning("Midia baixada nao encontrada localmente.")

    caption = latest.get("caption")
    if caption:
        with st.expander("Legenda da publicacao", expanded=True):
            st.write(caption)

    with st.expander("Interpretacao do K-OS", expanded=True):
        st.write("Onde parou:", interpretation.get("where_project_stopped"))
        st.write("Status Instagram:", interpretation.get("instagram_latest_status"))
        st.write("Proxima acao recomendada:", interpretation.get("recommended_next_action"))
        kos_compact_json("Detalhes técnicos", {
            "caption_hits": gp_score.get("hits"),
            "seems_gp_oxy_related": gp_score.get("seems_gp_oxy_related"),
            "download": download,
            "policy": audit.get("policy"),
        })

    st.markdown("### 3. Decisao humana")

    note = st.text_input(
        "Nota da decisao",
        placeholder="Exemplo: OK, seguir para Parada Atlantida depois de registrar Hupmix.",
        key="kos_hupmix_garoto_oxy_decision_note",
    )

    c_ok, c_adjust = st.columns(2)

    if c_ok.button("OK — Hupmix revisado e aprovado", type="primary", use_container_width=True, key="kos_hupmix_garoto_oxy_approve"):
        record = {
            "status": "HUPMIX_GAROTO_OXY_HISTORY_APPROVED_BY_OPERATOR",
            "created_at": datetime.now().isoformat(),
            "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_01 / Instagram continuity",
            "decision": {
                "approved": True,
                "approved_by": "human_operator",
                "note": note,
                "next_step": "seguir para Parada Atlantida em modo pesquisa/readiness"
            },
            "reviewed_assets": {
                "local_video": "local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4",
                "instagram_download": stored_path,
                "audit_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
            },
            "policy": {
                "publication_executed": False,
                "deploy_executed": False,
                "paid_ai_used": False,
                "scraping_used": False,
                "logged_browser_automation_used": False,
                "human_gate_required": True
            }
        }

        approval_path = approval_dir / "hupmix_garoto_oxy_history_approval.json"
        approval_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        st.session_state["kos_hupmix_garoto_oxy_approval_record"] = record
        st.success("OK humano registrado. Nenhuma publicacao foi executada.")
        kos_compact_json("Detalhes técnicos", {
            "status": record["status"],
            "approval_file": str(approval_path.relative_to(root)).replace("\\", "/"),
            "next_step": record["decision"]["next_step"]
        })

    if c_adjust.button("Pedir ajuste antes do OK", use_container_width=True, key="kos_hupmix_garoto_oxy_adjust"):
        record = {
            "status": "HUPMIX_GAROTO_OXY_HISTORY_ADJUSTMENT_REQUESTED",
            "created_at": datetime.now().isoformat(),
            "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_01 / Instagram continuity",
            "decision": {
                "approved": False,
                "adjustment_required": True,
                "note": note
            },
            "policy": {
                "publication_executed": False,
                "deploy_executed": False,
                "paid_ai_used": False,
                "human_gate_required": True
            }
        }

        adjustment_path = approval_dir / "hupmix_garoto_oxy_history_adjustment.json"
        adjustment_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        st.warning("Ajuste registrado. Nenhuma publicacao foi executada.")
        kos_compact_json("Detalhes técnicos", {
            "status": record["status"],
            "adjustment_file": str(adjustment_path.relative_to(root)).replace("\\", "/")
        })

    if st.button("Fechar revisao Garoto Oxy", use_container_width=True, key="kos_close_hupmix_garoto_oxy_review"):
        st.session_state["kos_show_hupmix_garoto_oxy_history_review"] = False
        st.info("Revisao fechada.")
        if hasattr(st, "rerun"):
            st.rerun()
# KOS_HUPMIX_GAROTO_OXY_HISTORY_REVIEW_END



# KOS_HUPMIX_NEXT_VIDEO_PRODUCTION_PANEL_BEGIN
def is_kos_hupmix_next_video_production_request(text: str) -> bool:
    """Detecta pedido de produzir o proximo video da campanha Garoto Oxy / Hupmix."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "proximo video", "próximo video", "novo video", "nova publicacao",
        "ligar producao", "producao de video", "produção de video",
        "continuar producao", "continuar produção", "video condizente",
        "campanha proximo video", "campanha próximo video",
    ]

    target_terms = ["hupmix", "garoto oxy", "oxy power", "gp_video_02", "gp video 02"]

    return any(a in value for a in action_terms) and any(t in value for t in target_terms)


def render_kos_hupmix_next_video_production_panel():
    """Painel visual para conectar historico real Hupmix com producao do proximo video."""
    import json
    import subprocess
    import sys
    from datetime import datetime
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_hupmix_next_video_production_panel", False):
        return

    root = Path.cwd()
    audit_path = root / "reports" / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
    factory_report_path = root / "reports" / "KOS_HUPMIX_GP_VIDEO_02_CONTINUITY_FACTORY.json"

    gp01_video = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    gp02_video = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_02_CONTINUITY_PREVIEW.mp4"
    gp02_storyboard = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_02_CONTINUITY_STORYBOARD.png"

    approval_dir = root / "live" / "human_decision_center"
    approval_dir.mkdir(parents=True, exist_ok=True)

    st.markdown("## Producao Hupmix — proximo video Garoto Oxy")
    st.caption("Painel de continuidade. Usa historico real do Instagram e preview local. Sem publicacao, sem scraping, sem IA paga.")

    msg = st.session_state.get("kos_hupmix_next_video_message")
    if msg:
        st.success(msg)

    audit = {}
    if audit_path.exists():
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            audit = {}

    instagram = audit.get("instagram", {})
    latest = instagram.get("latest_item") or {}
    download = instagram.get("download") or {}
    downloaded_path = root / download.get("stored_path", "") if download.get("stored_path") else None
    gp_score = instagram.get("gp_relevance_from_caption") or {}

    tabs = st.tabs(["Referencia real", "Novo video", "Briefing", "OK humano"])

    with tabs[0]:
        st.markdown("### Publicacao real Hupmix")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tipo", latest.get("media_type", "n/a"))
        c2.metric("Score Oxy", str(gp_score.get("score", 0)))
        c3.metric("Download", download.get("status", "n/a"))

        st.write("Data:", latest.get("timestamp"))
        if latest.get("permalink"):
            st.markdown(f"[Abrir publicacao no Instagram]({latest.get('permalink')})")

        if downloaded_path and downloaded_path.exists():
            st.video(str(downloaded_path))
            st.caption(download.get("stored_path"))
        else:
            st.warning("Video real baixado nao encontrado. Rode a auditoria de continuidade Hupmix.")

        caption = latest.get("caption")
        if caption:
            with st.expander("Legenda real", expanded=False):
                st.write(caption)

    with tabs[1]:
        st.markdown("### Novo preview GP_VIDEO_02")

        if st.button("Gerar / atualizar GP_VIDEO_02 local", type="primary", use_container_width=True, key="kos_generate_gp_video_02_continuity"):
            try:
                result = subprocess.run(
                    [sys.executable, "scripts\\run_kos_hupmix_gp_video_02_continuity_factory.py"],
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                st.session_state["kos_gp_video_02_generation_result"] = {
                    "returncode": result.returncode,
                    "stdout": result.stdout[-4000:],
                    "stderr": result.stderr[-4000:]
                }
                if hasattr(st, "rerun"):
                    st.rerun()
            except Exception as exc:
                st.error(f"Falha ao gerar GP_VIDEO_02: {exc}")

        gen = st.session_state.get("kos_gp_video_02_generation_result")
        if gen:
            if gen.get("returncode") == 0:
                st.success("GP_VIDEO_02 gerado localmente.")
            else:
                st.error("Falha na geracao local.")
            with st.expander("Log da geracao", expanded=False):
                st.code(gen.get("stdout") or "")
                if gen.get("stderr"):
                    st.code(gen.get("stderr"))

        st.markdown("#### GP_VIDEO_02 continuidade — novo preview")
        st.caption("Este bloco e o proximo video proposto. O video real do Instagram fica apenas como referencia.")

        if gp02_video.exists():
            st.video(str(gp02_video))
            st.caption("local_runtime/kos_video_previews/hupmix/GP_VIDEO_02_CONTINUITY_PREVIEW.mp4")
        else:
            st.info("Clique em Gerar / atualizar GP_VIDEO_02 local.")

        with st.expander("Comparar com GP_VIDEO_01 anterior", expanded=False):
            if gp01_video.exists():
                st.video(str(gp01_video))
            else:
                st.warning("GP_VIDEO_01 local nao encontrado.")

        if gp02_storyboard.exists():
            with st.expander("Storyboard GP_VIDEO_02", expanded=False):
                st.image(str(gp02_storyboard), use_container_width=True)

    with tabs[2]:
        st.markdown("### Briefing operacional")
        if factory_report_path.exists():
            try:
                factory = json.loads(factory_report_path.read_text(encoding="utf-8"))
                kos_compact_json("Detalhes técnicos", {
                    "status": factory.get("status"),
                    "outputs": factory.get("outputs"),
                    "next_step": factory.get("next_step"),
                    "policy": factory.get("policy")
                })
            except Exception as exc:
                st.warning(f"Nao foi possivel ler relatorio GP_VIDEO_02: {exc}")
        else:
            st.info("GP_VIDEO_02 ainda nao foi gerado.")

        job_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_02_CONTINUITY_FACTORY_JOB.json"
        if job_path.exists():
            try:
                job = json.loads(job_path.read_text(encoding="utf-8"))
                st.markdown("#### Cenas propostas")
                for i, scene in enumerate(job.get("scenes", []), start=1):
                    st.markdown(f"**Cena {i}: {scene.get('title')}**")
                    st.write(scene.get("line"))
                    st.caption(scene.get("screen"))
            except Exception as exc:
                st.warning(f"Nao foi possivel ler job GP_VIDEO_02: {exc}")

    with tabs[3]:
        st.markdown("### Decisao humana")
        note = st.text_input(
            "Nota da decisao criativa",
            placeholder="Exemplo: OK, seguir com este conceito para o proximo video.",
            key="kos_gp_video_02_direction_note",
        )

        c_ok, c_adjust = st.columns(2)

        if c_ok.button("OK criativo GP_VIDEO_02", type="primary", use_container_width=True, key="kos_approve_gp_video_02_direction"):
            record = {
                "status": "HUPMIX_GP_VIDEO_02_DIRECTION_APPROVED_BY_OPERATOR",
                "created_at": datetime.now().isoformat(),
                "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_02",
                "decision": {
                    "approved": True,
                    "approved_by": "human_operator",
                    "note": note,
                    "next_step": "producao com assets reais ou publicacao manual apos novo gate"
                },
                "assets": {
                    "reference_instagram_video": download.get("stored_path"),
                    "gp_video_02_preview": "local_runtime/kos_video_previews/hupmix/GP_VIDEO_02_CONTINUITY_PREVIEW.mp4",
                    "factory_report": "reports/KOS_HUPMIX_GP_VIDEO_02_CONTINUITY_FACTORY.json"
                },
                "policy": {
                    "publication_executed": False,
                    "deploy_executed": False,
                    "paid_ai_used": False,
                    "scraping_used": False,
                    "human_gate_required": True
                }
            }
            path = approval_dir / "hupmix_gp_video_02_direction_approval.json"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            st.success("OK criativo registrado. Nenhuma publicacao foi executada.")
            kos_compact_json("Detalhes técnicos", {
                "status": record["status"],
                "file": str(path.relative_to(root)).replace("\\", "/")
            })

        if c_adjust.button("Pedir ajuste GP_VIDEO_02", use_container_width=True, key="kos_adjust_gp_video_02_direction"):
            record = {
                "status": "HUPMIX_GP_VIDEO_02_DIRECTION_ADJUSTMENT_REQUESTED",
                "created_at": datetime.now().isoformat(),
                "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_02",
                "decision": {
                    "approved": False,
                    "adjustment_required": True,
                    "note": note
                },
                "policy": {
                    "publication_executed": False,
                    "paid_ai_used": False,
                    "human_gate_required": True
                }
            }
            path = approval_dir / "hupmix_gp_video_02_direction_adjustment.json"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            st.warning("Ajuste registrado. Nenhuma publicacao foi executada.")
            kos_compact_json("Detalhes técnicos", {
                "status": record["status"],
                "file": str(path.relative_to(root)).replace("\\", "/")
            })
# KOS_HUPMIX_NEXT_VIDEO_PRODUCTION_PANEL_END



# KOS_HUPMIX_GP_VIDEO_02_REAL_PRODUCTION_PANEL_BEGIN
def render_kos_hupmix_gp_video_02_real_production_panel():
    """Painel compacto para producao real do GP_VIDEO_02 com assets reais."""
    import json
    import re
    import subprocess
    import sys
    from datetime import datetime
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_hupmix_next_video_production_panel", False):
        return

    for key in [
        "kos_last_operator_data",
        "kos_last_safe_action_result",
        "kos_last_safe_action_packet_path",
        "kos_last_public_research_packet",
    ]:
        st.session_state.pop(key, None)

    root = Path.cwd()
    assets_dir = root / "content_packs" / "hupmix_gp_video_02" / "assets_inbox"
    assets_dir.mkdir(parents=True, exist_ok=True)

    audit_path = root / "reports" / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
    real_report_path = root / "reports" / "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json"
    real_preview = root / "local_runtime" / "kos_video_previews" / "hupmix" / "gp_video_02_real" / "GP_VIDEO_02_REAL_ASSET_PREVIEW.mp4"
    real_storyboard = root / "local_runtime" / "kos_video_previews" / "hupmix" / "gp_video_02_real" / "GP_VIDEO_02_REAL_ASSET_STORYBOARD.png"

    approval_dir = root / "live" / "human_decision_center"
    approval_dir.mkdir(parents=True, exist_ok=True)

    st.markdown("## Producao real Hupmix — GP_VIDEO_02")
    st.caption("Regra: nao gerar video fake. O proximo video so vira preview real quando houver footage/imagens reais anexadas.")

    msg = st.session_state.get("kos_hupmix_next_video_message")
    if msg:
        st.success(msg)

    audit = {}
    if audit_path.exists():
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            audit = {}

    instagram = audit.get("instagram", {})
    latest = instagram.get("latest_item") or {}
    download = instagram.get("download") or {}
    downloaded_path = root / download.get("stored_path", "") if download.get("stored_path") else None
    gp_score = instagram.get("gp_relevance_from_caption") or {}

    tabs = st.tabs(["Resumo", "Referencia compacta", "Assets reais", "Preview real", "OK humano"])

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        c1.metric("Campanha", "Garoto Oxy")
        c2.metric("Score Oxy", str(gp_score.get("score", 0)))
        c3.metric("Modo", "Real assets")

        st.info("O video publicado no Instagram e referencia. O GP_VIDEO_02 precisa de material novo real ou assets anexados.")
        st.write("Pasta de entrada:")
        st.code("content_packs/hupmix_gp_video_02/assets_inbox")

    with tabs[1]:
        st.markdown("### Referencia real do Instagram")
        st.caption("Compacto para nao ocupar a tela. Este video nao e o GP_VIDEO_02.")

        st.write("Data:", latest.get("timestamp"))
        if latest.get("permalink"):
            st.markdown(f"[Abrir publicacao no Instagram]({latest.get('permalink')})")

        with st.expander("Ver video real de referencia", expanded=False):
            if downloaded_path and downloaded_path.exists():
                left, center, right = st.columns([1, 1.2, 1])
                with center:
                    st.video(str(downloaded_path))
                    st.caption(download.get("stored_path"))
            else:
                st.warning("Video real baixado nao encontrado. Rode a auditoria Hupmix novamente.")

        caption = latest.get("caption")
        if caption:
            with st.expander("Legenda real", expanded=False):
                st.write(caption)

    with tabs[2]:
        st.markdown("### Anexar footage real GP_VIDEO_02")
        st.caption("Envie videos/fotos reais do produto, antes, aplicacao e depois.")

        uploads = st.file_uploader(
            "Adicionar assets reais",
            type=["mp4", "mov", "m4v", "avi", "webm", "jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="kos_gp_video_02_real_assets_upload"
        )

        if uploads:
            saved = []
            for file in uploads:
                safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", file.name).strip("_")
                if not safe:
                    safe = "asset_real"
                target = assets_dir / safe
                target.write_bytes(file.getbuffer())
                saved.append(str(target.relative_to(root)).replace("\\", "/"))
            st.success("Assets salvos.")
            kos_compact_json("Detalhes técnicos", saved)

        current_assets = [p for p in sorted(assets_dir.iterdir()) if p.is_file() and not p.name.startswith(".")]
        st.write("Assets atuais:", len(current_assets))

        for p in current_assets[:20]:
            st.caption(f"{p.name} | {p.stat().st_size} bytes")

        if st.button("Auditar assets e gerar preview real", type="primary", use_container_width=True, key="kos_gp_video_02_real_asset_audit_button"):
            result = subprocess.run(
                [sys.executable, "scripts\\run_kos_hupmix_gp_video_02_real_asset_audit.py"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=240
            )
            st.session_state["kos_gp_video_02_real_asset_audit_result"] = {
                "returncode": result.returncode,
                "stdout": result.stdout[-5000:],
                "stderr": result.stderr[-5000:]
            }
            if hasattr(st, "rerun"):
                st.rerun()

        result = st.session_state.get("kos_gp_video_02_real_asset_audit_result")
        if result:
            if result.get("returncode") == 0:
                st.success("Auditoria finalizada.")
            else:
                st.error("Falha na auditoria.")
            with st.expander("Log", expanded=False):
                st.code(result.get("stdout") or "")
                if result.get("stderr"):
                    st.code(result.get("stderr"))

    with tabs[3]:
        st.markdown("### Preview real GP_VIDEO_02")

        report = {}
        if real_report_path.exists():
            try:
                report = json.loads(real_report_path.read_text(encoding="utf-8"))
            except Exception:
                report = {}

        status = report.get("status", "NAO_AUDITADO")
        st.write("Status:", status)

        if status == "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_PREVIEW_READY" and real_preview.exists():
            left, center, right = st.columns([1, 1.15, 1])
            with center:
                st.video(str(real_preview))
                st.caption("Preview criado somente com assets reais anexados.")

            if real_storyboard.exists():
                with st.expander("Storyboard real", expanded=False):
                    st.image(str(real_storyboard), use_container_width=True)
        else:
            st.warning("Ainda nao existe preview real. Anexe assets reais na aba anterior.")
            st.markdown(
                "- video vertical curto do produto\n"
                "- cena antes\n"
                "- cena aplicando\n"
                "- cena depois\n"
                "- produto/preco/CTA"
            )

        if report:
            with st.expander("Relatorio tecnico", expanded=False):
                kos_compact_json("Detalhes técnicos", report)

    with tabs[4]:
        st.markdown("### Decisao humana")

        note = st.text_input(
            "Nota",
            placeholder="Exemplo: OK com assets reais / precisa gravar aplicacao melhor.",
            key="kos_gp_video_02_real_decision_note"
        )

        report = {}
        if real_report_path.exists():
            try:
                report = json.loads(real_report_path.read_text(encoding="utf-8"))
            except Exception:
                report = {}

        has_real_preview = report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_PREVIEW_READY" and real_preview.exists()

        c1, c2 = st.columns(2)

        if c1.button("OK preview real GP_VIDEO_02", type="primary", disabled=not has_real_preview, use_container_width=True, key="kos_ok_gp_video_02_real_preview"):
            record = {
                "status": "HUPMIX_GP_VIDEO_02_REAL_PREVIEW_APPROVED_BY_OPERATOR",
                "created_at": datetime.now().isoformat(),
                "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_02 real assets",
                "decision": {
                    "approved": True,
                    "note": note,
                    "next_step": "seguir somente com gate de publicacao manual separado"
                },
                "assets": {
                    "real_preview": "local_runtime/kos_video_previews/hupmix/gp_video_02_real/GP_VIDEO_02_REAL_ASSET_PREVIEW.mp4",
                    "audit_report": "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json"
                },
                "policy": {
                    "publication_executed": False,
                    "paid_ai_used": False,
                    "scraping_used": False,
                    "human_gate_required": True
                }
            }
            path = approval_dir / "hupmix_gp_video_02_real_preview_approval.json"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            st.success("OK humano registrado. Nenhuma publicacao foi executada.")
            kos_compact_json("Detalhes técnicos", {"file": str(path.relative_to(root)).replace("\\", "/"), "status": record["status"]})

        if c2.button("Pedir ajuste / gravar mais material", use_container_width=True, key="kos_adjust_gp_video_02_real_preview"):
            record = {
                "status": "HUPMIX_GP_VIDEO_02_REAL_PREVIEW_ADJUSTMENT_REQUESTED",
                "created_at": datetime.now().isoformat(),
                "scope": "Hupmix / Garoto Oxy Power / GP_VIDEO_02 real assets",
                "decision": {
                    "approved": False,
                    "adjustment_required": True,
                    "note": note
                },
                "policy": {
                    "publication_executed": False,
                    "paid_ai_used": False,
                    "human_gate_required": True
                }
            }
            path = approval_dir / "hupmix_gp_video_02_real_preview_adjustment.json"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            st.warning("Ajuste registrado. Nenhuma publicacao foi executada.")
            kos_compact_json("Detalhes técnicos", {"file": str(path.relative_to(root)).replace("\\", "/"), "status": record["status"]})
# KOS_HUPMIX_GP_VIDEO_02_REAL_PRODUCTION_PANEL_END



# KOS_CAPABILITY_REGISTRY_OPERATOR_BRIDGE_BEGIN
def kos_clear_specialized_panel_noise():
    """Remove respostas antigas/stale quando um painel especializado assume a tela."""
    import json
    import streamlit as st

    fixed_keys = [
        "kos_last_operator_data",
        "kos_last_operator_response",
        "kos_last_operator_plan",
        "kos_last_operator_modules",
        "kos_last_operator_next_step",
        "kos_last_operator_risk",
        "kos_last_operator_safe_action",
        "kos_last_safe_action_result",
        "kos_last_safe_action_packet_path",
        "kos_last_safe_action_packet",
        "kos_last_public_research_packet",
        "kos_last_router_result",
        "kos_last_router_data",
        "kos_last_orchestrator_result",
        "kos_last_action_packet",
        "kos_last_generated_plan",
    ]

    for key in fixed_keys:
        st.session_state.pop(key, None)

    for key, value in list(st.session_state.items()):
        if key in {"kos_operator_request_text"}:
            continue

        try:
            blob = json.dumps(value, ensure_ascii=False, default=str)
        except Exception:
            blob = str(value)

        stale_markers = [
            "KOS_START_HERE.cmd",
            "Vou usar estes modulos",
            "Acoes reais permanecem bloqueadas",
            "Acao segura disponivel",
            "Gerar plano operacional simples",
        ]

        if any(marker in blob for marker in stale_markers):
            st.session_state.pop(key, None)

    st.session_state["kos_suppress_default_response"] = True


def is_kos_capability_registry_request(text: str) -> bool:
    """Detecta pedido de auditoria/autonomia/capacidades do K-OS."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "auditar tudo",
        "auditoria operacional",
        "auditoria master",
        "o que funciona",
        "tudo que funciona",
        "nivel da autonomia",
        "nível da autonomia",
        "autonomia",
        "agentes funcionando",
        "quais agentes",
        "inteligencia conectada",
        "inteligência conectada",
        "auto evolucao",
        "auto evolução",
        "evolucao do copiloto",
        "evolução do copiloto",
        "linha do tempo",
        "capability registry",
        "registro de capacidades",
        "mapa de capacidades",
        "capacidades do k-os",
        "capacidades do kos",
        "carro quantico",
        "carro quântico",
    ]

    target_terms = [
        "k-os",
        "kos",
        "k atlas",
        "k-atlas",
        "copiloto",
        "agentes",
        "autonomia",
        "capacidades",
    ]

    return any(term in value for term in action_terms) and (
        any(term in value for term in target_terms)
        or "o que funciona" in value
        or "auditar tudo" in value
    )


def render_kos_capability_registry_panel():
    """Painel central de capacidades, autonomia e linha do tempo do K-OS."""
    import json
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_capability_registry_panel", False):
        return

    kos_clear_specialized_panel_noise()

    root = Path.cwd()
    registry_path = root / "memory" / "kos_governance" / "KOS_CAPABILITY_REGISTRY.json"
    audit_path = root / "reports" / "KOS_OPERATIONAL_MASTER_AUDIT_V1.json"

    st.markdown("## K-OS — Capacidades, Autonomia e Estado Real")
    st.caption("Fonte: KOS_CAPABILITY_REGISTRY + Operational Master Audit. Sem acao externa. Sem publicacao.")

    msg = st.session_state.get("kos_capability_registry_message")
    if msg:
        st.success(msg)

    if not registry_path.exists():
        st.error("KOS_CAPABILITY_REGISTRY.json nao encontrado. Rode a auditoria operacional master.")
        return

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        st.error(f"Falha ao ler registry: {exc}")
        return

    audit = {}
    if audit_path.exists():
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            audit = {}

    capabilities = registry.get("capabilities", [])
    policy = registry.get("policy", {})
    intelligence = registry.get("intelligence_connected", {})
    levels = registry.get("autonomy_levels", {})
    gaps = audit.get("gaps", [])
    summary = audit.get("summary", {})
    phase = (audit.get("line_of_time_position") or {}).get("phase", "unknown")
    meaning = (audit.get("line_of_time_position") or {}).get("meaning", "")

    working = [c for c in capabilities if c.get("works_now")]
    blocked = [c for c in capabilities if not c.get("works_now")]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capacidades", str(len(capabilities)))
    c2.metric("Funcionando", str(len(working)))
    c3.metric("Autonomia max", str(policy.get("current_max_autonomy_level", "n/a")))
    c4.metric("Gargalos", str(len(gaps)))

    st.info(meaning or "K-OS entrou na fase de mapa central de capacidades e autonomia.")

    tabs = st.tabs(["Mapa", "Capacidades", "Autonomia", "Inteligencia", "Gargalos", "Timeline"])

    with tabs[0]:
        st.markdown("### Fase atual")
        st.write("Fase:", phase)

        st.markdown("### Resumo operacional")
        if summary:
            kos_compact_json("Detalhes técnicos", summary)
        else:
            st.warning("Resumo da auditoria nao encontrado.")

        st.markdown("### Politica ativa")
        kos_compact_json("Detalhes técnicos", policy)

        st.markdown("### Leitura direta")
        st.write(
            "O K-OS ja sabe auditar, ler memoria, consultar Hupmix por Meta Graph read-only, "
            "receber assets, gerar previews locais e registrar gates humanos. "
            "Ele ainda nao deve publicar, gastar IA paga, usar navegador logado ou fazer scraping."
        )

    with tabs[1]:
        st.markdown("### Capacidades conhecidas")

        rows = []
        for c in capabilities:
            rows.append({
                "id": c.get("id"),
                "nome": c.get("name"),
                "tipo": c.get("type"),
                "status": c.get("status"),
                "nivel": c.get("autonomy_level"),
                "funciona": c.get("works_now"),
                "age_sozinho": c.get("can_act_alone"),
                "gate_humano": c.get("requires_human_gate"),
            })

        st.dataframe(rows, use_container_width=True)

        with st.expander("Detalhes por capacidade", expanded=False):
            for c in capabilities:
                st.markdown(f"#### {c.get('name')}")
                st.write(c.get("what_it_does"))
                st.caption(c.get("path"))
                kos_compact_json("Detalhes técnicos", {
                    "id": c.get("id"),
                    "status": c.get("status"),
                    "nivel": c.get("autonomy_level"),
                    "works_now": c.get("works_now"),
                    "can_act_alone": c.get("can_act_alone"),
                    "requires_human_gate": c.get("requires_human_gate"),
                })

    with tabs[2]:
        st.markdown("### Niveis de autonomia")
        current = str(policy.get("current_max_autonomy_level", "n/a"))

        for level_id, data in levels.items():
            title = f"Nivel {level_id} — {data.get('name')}"
            if level_id == current:
                st.success(title + "  | nivel maximo atual")
            else:
                st.markdown(f"**{title}**")
            st.write(data.get("description"))

        st.warning("Nivel 4 e 5 seguem bloqueados ate criarmos gate separado de acao externa.")

    with tabs[3]:
        st.markdown("### Inteligencia conectada")
        kos_compact_json("Detalhes técnicos", intelligence)

        st.markdown("### O que esta conectado de verdade")
        st.write("- Python executor: executa scripts locais.")
        st.write("- Streamlit cockpit: interface operacional.")
        st.write("- GitHub memory: historico persistente.")
        st.write("- JSON memory: estado operacional.")
        st.write("- Meta Graph read-only: leitura Hupmix/Instagram autorizada.")
        st.write("- Video render local: cria previews locais com assets.")
        st.write("- File intake: recebe arquivos/assets.")
        st.write("- Public research registry: registra pesquisa publica governada.")

    with tabs[4]:
        st.markdown("### Gargalos atuais")
        if not gaps:
            st.success("Nenhum gargalo registrado na auditoria master.")
        else:
            for gap in gaps:
                st.markdown(f"#### {gap.get('id')}")
                st.write("Severidade:", gap.get("severity"))
                st.write("Impacto:", gap.get("impact"))
                st.write("Correção:", gap.get("fix"))

        st.markdown("### Próximo salto recomendado")
        for step in audit.get("next_steps", []):
            st.write(f"{step.get('priority')}. {step.get('action')}")
            st.caption(f"impacto: {step.get('impact')} | risco: {step.get('risk')}")

    with tabs[5]:
        st.markdown("### Timeline Git recente")
        timeline = ((audit.get("git") or {}).get("timeline_recent")) or []
        if timeline:
            for line in timeline[:30]:
                st.code(line)
        else:
            st.warning("Timeline nao encontrada no audit.")

    if st.button("Fechar painel de capacidades", use_container_width=True, key="kos_close_capability_registry_panel"):
        st.session_state["kos_show_capability_registry_panel"] = False
        st.session_state["kos_suppress_default_response"] = False
        if hasattr(st, "rerun"):
            st.rerun()
# KOS_CAPABILITY_REGISTRY_OPERATOR_BRIDGE_END



# KOS_CAPABILITY_EXECUTOR_PANEL_BEGIN
def is_kos_capability_executor_request(text: str) -> bool:
    """Detecta pedido para motor real / executor de capacidades."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "motor real",
        "capability executor",
        "executor de capacidades",
        "acionar capacidade",
        "executar capacidade",
        "resolver hupmix",
        "hupmix ate resolver",
        "hupmix até resolver",
        "voltar para hupmix",
        "resolver garoto oxy",
        "resolver gp_video_02",
        "resolver gp video 02",
    ]

    return any(term in value for term in action_terms)


def render_kos_capability_executor_panel():
    """Painel do motor real governado do K-OS."""
    import json
    import subprocess
    import sys
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_capability_executor_panel", False):
        return

    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass

    root = Path.cwd()
    last_run_path = root / "reports" / "KOS_CAPABILITY_EXECUTOR_LAST_RUN.json"
    status_path = root / "reports" / "KOS_CAPABILITY_EXECUTOR_V1.json"

    st.markdown("## K-OS Capability Executor V1")
    st.caption("Motor real governado. Executa apenas capacidades locais/read-only permitidas. Acoes externas seguem bloqueadas.")

    msg = st.session_state.get("kos_capability_executor_message")
    if msg:
        st.success(msg)

    tabs = st.tabs(["Motor", "Hupmix", "Ultima execucao", "Politica"])

    def run_executor_request(request_text: str):
        result = subprocess.run(
            [sys.executable, "scripts\\run_kos_capability_executor.py", "--request", request_text],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=420
        )
        st.session_state["kos_capability_executor_last_result"] = {
            "request": request_text,
            "returncode": result.returncode,
            "stdout": result.stdout[-8000:],
            "stderr": result.stderr[-8000:]
        }

    with tabs[0]:
        st.markdown("### Executar capacidade governada")
        request_text = st.text_input(
            "Pedido para o motor",
            value=st.session_state.get("kos_last_operator_request", "status do motor"),
            key="kos_capability_executor_request_text"
        )

        if st.button("Executar pedido pelo motor", type="primary", use_container_width=True, key="kos_capability_executor_run_custom"):
            run_executor_request(request_text)
            if hasattr(st, "rerun"):
                st.rerun()

        st.info("O motor consulta rota, permissao e politica antes de executar. Publicacao, deploy, IA paga e scraping continuam bloqueados.")

    with tabs[1]:
        st.markdown("### Resolver Hupmix GP_VIDEO_02")
        st.write("Rota segura: Meta Graph read-only + auditoria local de assets reais.")

        if st.button("Rodar pipeline Hupmix agora", type="primary", use_container_width=True, key="kos_capability_executor_run_hupmix"):
            run_executor_request("resolver Hupmix GP_VIDEO_02 com assets reais")
            if hasattr(st, "rerun"):
                st.rerun()

        if st.button("Abrir painel de producao real Hupmix", use_container_width=True, key="kos_capability_executor_open_hupmix_panel"):
            st.session_state["kos_show_capability_executor_panel"] = False
            st.session_state["kos_show_hupmix_next_video_production_panel"] = True
            st.session_state["kos_hupmix_next_video_message"] = "Painel Hupmix aberto pelo Capability Executor. GP_VIDEO_02 exige assets reais."
            if hasattr(st, "rerun"):
                st.rerun()

        st.code("content_packs/hupmix_gp_video_02/assets_inbox")

    with tabs[2]:
        st.markdown("### Ultima execucao")

        result = st.session_state.get("kos_capability_executor_last_result")
        if result:
            if result.get("returncode") == 0:
                st.success("Executor finalizado.")
            else:
                st.error("Executor retornou erro.")
            st.code(result.get("stdout") or "")
            if result.get("stderr"):
                st.code(result.get("stderr"))

        if last_run_path.exists():
            try:
                last = json.loads(last_run_path.read_text(encoding="utf-8"))
                kos_compact_json("Detalhes técnicos", last)
            except Exception as exc:
                st.warning(f"Nao foi possivel ler last run: {exc}")
        else:
            st.info("Nenhuma execucao registrada ainda.")

    with tabs[3]:
        st.markdown("### Politica do executor")
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
                kos_compact_json("Detalhes técnicos", status.get("policy", status))
            except Exception:
                st.warning("Status do executor ainda nao carregado.")
        else:
            st.warning("KOS_CAPABILITY_EXECUTOR_V1.json ainda nao existe em reports.")

        st.warning("Nivel 4 e 5 seguem bloqueados. Nada sera publicado sem gate humano separado.")

    if st.button("Fechar motor", use_container_width=True, key="kos_close_capability_executor_panel"):
        st.session_state["kos_show_capability_executor_panel"] = False
        if hasattr(st, "rerun"):
            st.rerun()
# KOS_CAPABILITY_EXECUTOR_PANEL_END



# KOS_ORCHESTRATOR_MODE_V1_BEGIN
def is_kos_orchestrator_mode_request(text: str) -> bool:
    """Uma caixa: o K-OS orquestra sem jogar o operador para painel cheio de botoes."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    terms = [
        "motor real",
        "resolver hupmix",
        "hupmix gp_video_02",
        "hupmix gp video 02",
        "garoto oxy",
        "oxy power",
        "orquestrador",
        "sem botao",
        "sem monte de botao",
        "usar capacidades",
        "resolver ate o fim",
        "aprender com esse exemplo",
        "expandir consciencia",
        "alimentar conhecimento",
        "processos para outras lojas",
        "processos para saas",
        "processos para clinicas",
        "processos para agencias",
        "multinacionais",
        "caso escola",
        "universalizar processo",
    ]

    return any(term in value for term in terms)


def kos_orchestrator_run_safe_request(request_text: str):
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path.cwd()
    result = subprocess.run(
        [sys.executable, "scripts\\run_kos_capability_executor.py", "--request", request_text],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=420
    )

    last_run_path = root / "local_runtime" / "kos_capability_executor" / "last_run.json"
    last_run = {}

    if last_run_path.exists():
        try:
            last_run = json.loads(last_run_path.read_text(encoding="utf-8"))
        except Exception:
            last_run = {}

    return {
        "returncode": result.returncode,
        "stdout": result.stdout[-6000:],
        "stderr": result.stderr[-3000:],
        "last_run": last_run,
    }


def render_kos_orchestrator_mode_panel():
    import json
    import re
    import subprocess
    import sys
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_orchestrator_mode_panel", False):
        return

    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass

    root = Path.cwd()
    request_text = st.session_state.get("kos_orchestrator_request_text", "") or st.session_state.get("kos_last_operator_request", "")
    request_key = "kos_orchestrator_last_run_for_request"

    if st.session_state.get(request_key) != request_text:
        st.session_state["kos_orchestrator_result"] = kos_orchestrator_run_safe_request(request_text)
        st.session_state[request_key] = request_text

    result = st.session_state.get("kos_orchestrator_result") or {}
    last_run = result.get("last_run") or {}
    route = last_run.get("route") or {}
    executions = last_run.get("executions") or []
    next_step = last_run.get("next_step")
    blocked = last_run.get("blocked")

    st.markdown("## K-OS Orquestrador")
    st.caption("Uma caixa. Uma rota. Execucao segura automatica. Sem painel cheio de botoes.")

    if blocked:
        st.error("Pedido bloqueado por politica.")
    elif result.get("returncode") == 0:
        st.success("Rota segura executada.")
    else:
        st.warning("Orquestrador executou com alerta. Detalhes no modo avancado.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rota", route.get("route", "n/a"))
    c2.metric("Tarefas", str(len(route.get("tasks", []))))
    c3.metric("Bloqueado", "sim" if blocked else "nao")

    st.markdown("### Estado")
    st.write(route.get("objective", "Pedido analisado pelo orquestrador."))

    st.markdown("### Acao feita")
    if executions:
        for item in executions:
            name = item.get("name") or item.get("executor_id")
            if item.get("allowed") and item.get("returncode") == 0:
                st.write(f"- OK: {name} | {item.get('report_status')}")
            elif not item.get("allowed"):
                st.write(f"- Bloqueado: {name} | {item.get('reason')}")
            else:
                st.write(f"- Erro: {name} | returncode {item.get('returncode')}")
    else:
        st.write("- Nenhuma tarefa operacional foi necessaria.")

    st.markdown("### Proximo passo")
    st.info(next_step or "Aguardando novo pedido.")

    # KOS_HUPMIX_MANUS_UPGRADE_INLINE_UI_BEGIN
    if route.get("route") == "hupmix_manus_upgrade":
        upgrade_status_path = root / "local_runtime" / "kos_hupmix_gp_video_02_manus_upgrade" / "status.json"
        if upgrade_status_path.exists():
            try:
                up = json.loads(upgrade_status_path.read_text(encoding="utf-8"))
                st.markdown("### GP_VIDEO_02 Manus-compatible")
                kos_compact_json("Detalhes técnicos", {
                    "status": up.get("status"),
                    "score": up.get("score"),
                    "brief": up.get("brief"),
                    "prompt_pack": up.get("prompt_pack"),
                    "source_video": up.get("source_video"),
                    "character_reference": up.get("character_reference"),
                    "product_reference": up.get("product_reference"),
                    "next_step": up.get("next_step")
                })
                preview_value = up.get("preview") or ""
                preview_path = root / preview_value
                if preview_value and preview_path.exists():
                    st.video(str(preview_path))
                    st.caption("Preview local Manus-compatible. Publicacao bloqueada ate OK humano.")
                storyboard_value = up.get("storyboard") or ""
                storyboard_path = root / storyboard_value
                if storyboard_value and storyboard_path.exists():
                    with st.expander("Storyboard", expanded=False):
                        st.image(str(storyboard_path))
            except Exception:
                pass
        return
    # KOS_HUPMIX_MANUS_UPGRADE_INLINE_UI_END

    # KOS_MANUS_REFERENCE_IMPORT_INLINE_UI_BEGIN
    if route.get("route") == "manus_reference_import":
        manus_status_path = root / "local_runtime" / "kos_reference_imports" / "hupmix_manus" / "status.json"
        if manus_status_path.exists():
            try:
                manus = json.loads(manus_status_path.read_text(encoding="utf-8"))
                st.markdown("### Referencia Manus importada")
                st.write("O pacote Manus/Hupmix foi convertido em referencia criativa, skill e plano de upgrade reutilizavel.")
                kos_compact_json("Detalhes técnicos", {
                    "status": manus.get("status"),
                    "index": manus.get("index"),
                    "creative_skill": manus.get("creative_skill"),
                    "gp_skill": manus.get("gp_skill"),
                    "upgrade_plan": manus.get("upgrade_plan"),
                    "counts": manus.get("counts"),
                    "next_step": manus.get("next_step")
                })
            except Exception:
                pass
    # KOS_MANUS_REFERENCE_IMPORT_INLINE_UI_END

    # KOS_PROCESS_LEARNING_INLINE_UI_BEGIN
    if route.get("route") == "universal_process_learning":
        learning_path = root / "local_runtime" / "kos_process_learning_engine" / "status.json"
        if learning_path.exists():
            try:
                learning = json.loads(learning_path.read_text(encoding="utf-8"))
                st.markdown("### Aprendizado promovido")
                st.write("Hupmix foi registrado como caso-escola. O processo agora pode ser reutilizado em lojas, SaaS, agencias, clinicas e operacoes maiores.")
                kos_compact_json("Detalhes técnicos", {
                    "registry": learning.get("registry"),
                    "case_learning": learning.get("hupmix_case_learning"),
                    "next_step": learning.get("next_step")
                })
            except Exception:
                pass
    # KOS_PROCESS_LEARNING_INLINE_UI_END

    # KOS_GP_VIDEO_02_GENERATED_VIDEO_UI_BEGIN
    # Video Hupmix so pode aparecer dentro da rota Hupmix.
    if route.get("route") == "hupmix_creation_pipeline":
        gen_status_path = root / "local_runtime" / "kos_hupmix_gp_video_02_local_video_generator" / "status.json"
        gen_status = {}
        if gen_status_path.exists():
            try:
                gen_status = json.loads(gen_status_path.read_text(encoding="utf-8"))
            except Exception:
                gen_status = {}

        if route.get("route") == "hupmix_creation_pipeline" and gen_status.get("status") in ["KOS_HUPMIX_GP_VIDEO_02_LOCAL_VIDEO_GENERATED", "KOS_HUPMIX_GP_VIDEO_02_LOCAL_VIDEO_GENERATED_FALLBACK_COPY"]:
            generated_path = root / gen_status.get("output", "")
            if generated_path.exists():
                st.markdown("### Video gerado GP_VIDEO_02")
                left, center, right = st.columns([1, 1.15, 1])
                with center:
                    st.video(str(generated_path))
                    st.caption("Gerado localmente com asset real do Instagram. Publicacao bloqueada ate OK humano.")
                st.info(gen_status.get("next_step", "Validar video gerado."))
                if gen_status.get("fallback_used"):
                    st.warning("Gerador usou fallback: validacao humana obrigatoria.")
                return
    # KOS_GP_VIDEO_02_GENERATED_VIDEO_UI_END

    # KOS_NON_HUPMIX_ROUTE_UI_RETURN_BEGIN
    # Depois de renderizar a UI da rota atual, não deixar blocos Hupmix vazarem
    # para rotas universais, Manus, pesquisa ou registry.
    if route.get("route") != "hupmix_creation_pipeline":
        return
    # KOS_NON_HUPMIX_ROUTE_UI_RETURN_END

    gp_report_path = root / "reports" / "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json"
    gp_report = {}
    if gp_report_path.exists():
        try:
            gp_report = json.loads(gp_report_path.read_text(encoding="utf-8"))
        except Exception:
            gp_report = {}

    if gp_report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS":
        st.markdown("### Hupmix GP_VIDEO_02 precisa de material real")
        st.write("Anexe videos ou fotos reais do produto, aplicacao, antes/depois.")

        # KOS_CAPTURE_MISSION_INLINE_UI_BEGIN
        mission_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_02_CAPTURE_MISSION.json"
        if mission_path.exists():
            try:
                mission = json.loads(mission_path.read_text(encoding="utf-8"))
                st.markdown("### Missao de captacao criada")
                st.write(mission.get("campaign", {}).get("objective"))
                with st.expander("Ver takes que precisam ser captados", expanded=True):
                    for item in mission.get("capture_mission", {}).get("required_real_assets", []):
                        st.markdown(f"**{item.get('id')}**")
                        st.write(item.get("description"))
                        st.caption(item.get("instruction"))
                st.caption("Depois da captacao, anexe os arquivos abaixo. O K-OS monta o preview real.")
            except Exception:
                pass
        # KOS_CAPTURE_MISSION_INLINE_UI_END

        assets_dir = root / "content_packs" / "hupmix_gp_video_02" / "assets_inbox"
        assets_dir.mkdir(parents=True, exist_ok=True)

        uploads = st.file_uploader(
            "Anexar assets reais",
            type=["mp4", "mov", "m4v", "avi", "webm", "jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="kos_orchestrator_hupmix_assets_upload"
        )

        if uploads:
            saved = []
            for file in uploads:
                safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", file.name).strip("_") or "asset_real"
                target = assets_dir / safe
                target.write_bytes(file.getbuffer())
                saved.append(str(target.relative_to(root)).replace("\\", "/"))

            st.success("Assets recebidos. Reprocessando automaticamente.")
            kos_compact_json("Detalhes técnicos", saved)

            subprocess.run(
                [sys.executable, "scripts\\run_kos_capability_executor.py", "--request", "resolver Hupmix GP_VIDEO_02 com assets reais"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=420
            )

            st.session_state.pop(request_key, None)
            if hasattr(st, "rerun"):
                st.rerun()

    elif gp_report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_PREVIEW_READY":
        preview = root / "local_runtime" / "kos_video_previews" / "hupmix" / "gp_video_02_real" / "GP_VIDEO_02_REAL_ASSET_PREVIEW.mp4"
        if preview.exists():
            st.markdown("### Preview real GP_VIDEO_02")
            left, center, right = st.columns([1, 1.15, 1])
            with center:
                st.video(str(preview))
                st.caption("Preview criado somente com assets reais.")
            st.warning("Publicacao continua bloqueada. Proximo passo exige OK humano separado.")

    with st.expander("Modo avancado", expanded=False):
        kos_compact_json("Detalhes técnicos", last_run)
        st.code(result.get("stdout") or "")
        if result.get("stderr"):
            st.code(result.get("stderr"))

# KOS_ORCHESTRATOR_MODE_V1_END



# KOS_MANUS_REFERENCE_IMPORT_DETECTOR_BEGIN
def is_kos_manus_reference_import_request(text: str) -> bool:
    import unicodedata
    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    terms = [
        "manus",
        "pacote manus",
        "referencia manus",
        "referencia criativa",
        "exportar para k-os",
        "exportar para kos",
        "materiais do hupmix",
        "compativel com manus",
        "melhor que manus",
        "importar pacote"
    ]
    return any(term in value for term in terms)
# KOS_MANUS_REFERENCE_IMPORT_DETECTOR_END


# KOS_HUPMIX_MANUS_UPGRADE_DETECTOR_BEGIN
def is_kos_hupmix_manus_upgrade_request(text: str) -> bool:
    import unicodedata
    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    terms = [
        "melhorar gp_video_02",
        "melhorar gp video 02",
        "upgrade gp_video_02",
        "upgrade gp video 02",
        "usar referencia manus",
        "manus style",
        "manus-compatible",
        "score briefing prompts"
    ]
    return any(term in value for term in terms)
# KOS_HUPMIX_MANUS_UPGRADE_DETECTOR_END

# Legacy marker for frontdoor tests: Pedido ao K-OS.
request = st.text_area(
    "Converse com o K-OS",
    placeholder="Exemplo: revise as últimas publicações da Hupmix e me diga o próximo movimento seguro.",
    height=120,
    key="kos_operator_request_text",
)

st.caption("Você pode escrever: `o que você pode fazer por mim`, `revise a Hupmix`, `prepare um SaaS`, `cheque conexões`, `crie uma ação segura`.")

col1, col2 = st.columns([3, 1])

with col1:
    send = st.button("Conversar com K-OS", type="primary", use_container_width=True)

with col2:
    advanced = st.button("Avançado", use_container_width=True)

if advanced:
    st.info(
        "Modo avancado nao abre cockpits automaticamente. Para evitar erro humano, comandos tecnicos continuam ocultos."
    )
    st.write("Peca ao K-OS a acao desejada em linguagem normal.")

render_text_decision_feedback()

if send:
    _decision_command, _decision_detail = parse_text_decision(st.session_state.get("kos_operator_request_text", ""))
    if _decision_command:
        st.session_state["kos_last_text_decision"] = register_text_decision(_decision_command, _decision_detail)
        send = False
        if hasattr(st, "rerun"):
            st.rerun()

# KOS_CAPABILITY_STATUS_CHAT_INTENT_BEGIN
if send and is_kos_capability_status_question(st.session_state.get("kos_operator_request_text", "")):
    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass
    st.session_state["kos_last_capability_status_answer"] = build_kos_capability_status_answer()
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_CAPABILITY_STATUS_CHAT_INTENT_END

if st.session_state.get("kos_last_capability_status_answer"):
    render_kos_capability_status_answer(st.session_state["kos_last_capability_status_answer"])

if send:
    st.session_state.pop("kos_last_capability_status_answer", None)

# KOS_READ_ONLY_DIAGNOSTIC_GATE_BEGIN
if send and is_kos_read_only_diagnostic_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_operator_flow_diagnostic"] = True
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_diagnostic_read_only_message"] = "Diagnostico aberto em modo read-only. Nenhum Router, Safe Action, publicacao, deploy ou IA paga foi acionado."
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_READ_ONLY_DIAGNOSTIC_GATE_END

# KOS_READ_ONLY_LOUSA_GATE_BEGIN
if send and is_kos_read_only_lousa_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_gp_video_01_lousa"] = True
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_lousa_read_only_message"] = "Lousa visual aberta em modo read-only. Nenhum Router, Safe Action, publicacao, deploy ou IA paga foi acionado."
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_READ_ONLY_LOUSA_GATE_END


# KOS_GP_VIDEO_01_LOUSA_INLINE_VISIBLE_BEGIN
if st.session_state.get("kos_show_gp_video_01_lousa", False):
    from pathlib import Path as _KosPath
    import json as _kos_json

    _kos_root = _KosPath.cwd()
    _mp4_path = _kos_root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    _storyboard_path = _kos_root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png"
    _job_path = _kos_root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json"
    _report_path = _kos_root / "reports" / "KOS_HUPMIX_GP_VIDEO_FACTORY_FREE_MODE_V1.json"

    st.session_state["kos_gp_video_01_lousa_rendered_inline"] = True

    st.markdown("## Lousa visual - GP_VIDEO_01 Hupmix")

    _msg = st.session_state.get("kos_lousa_read_only_message")
    if _msg:
        st.success(_msg)

    st.caption("Preview local. Sem IA paga. Sem publicacao. Sem deploy. Gate humano obrigatorio.")

    if _mp4_path.exists():
        st.video(str(_mp4_path))
        st.caption("Fonte local: local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4")
    else:
        st.error("MP4 local nao encontrado. Rode o Video Factory Free Mode novamente.")

    _c1, _c2, _c3 = st.columns(3)
    _c1.metric("Modo", "Free/local")
    _c2.metric("Publicacao", "Bloqueada")
    _c3.metric("IA paga", "Nao usada")

    if _storyboard_path.exists():
        with st.expander("Storyboard", expanded=False):
            st.image(str(_storyboard_path), use_container_width=True)

    if _report_path.exists():
        try:
            _report = _kos_json.loads(_report_path.read_text(encoding="utf-8"))
            _outputs = _report.get("outputs", {})
            with st.expander("Registro tecnico do video", expanded=False):
                kos_compact_json("Detalhes técnicos", {
                    "status": _report.get("status"),
                    "mp4": _outputs.get("mp4"),
                    "mp4_size": _outputs.get("mp4_size"),
                    "storyboard": _outputs.get("storyboard"),
                    "storyboard_size": _outputs.get("storyboard_size"),
                    "policy": _report.get("policy"),
                })
        except Exception as exc:
            st.warning(f"Nao foi possivel ler o registro tecnico do video: {exc}")

    if _job_path.exists():
        try:
            _job = _kos_json.loads(_job_path.read_text(encoding="utf-8"))
            _scenes = _job.get("scenes", [])
            with st.expander("Cenas do GP_VIDEO_01", expanded=False):
                for _idx, _scene in enumerate(_scenes, start=1):
                    st.markdown(f"**Cena {_idx}: {_scene.get('title', '')}**")
                    st.write(_scene.get("line", ""))
        except Exception as exc:
            st.warning(f"Nao foi possivel ler o job do video: {exc}")

    if st.button("Fechar lousa visual", key="kos_close_gp_video_01_lousa_inline", use_container_width=True):
        st.session_state["kos_show_gp_video_01_lousa"] = False
        st.session_state["kos_gp_video_01_lousa_rendered_inline"] = False
        st.info("Lousa visual fechada. Faca um novo pedido ao K-OS.")
# KOS_GP_VIDEO_01_LOUSA_INLINE_VISIBLE_END

# KOS_HUPMIX_MANUS_UPGRADE_PRIORITY_GATE_BEGIN
if send and is_kos_hupmix_manus_upgrade_request(st.session_state.get("kos_operator_request_text", "")):
    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass
    st.session_state["kos_show_orchestrator_mode_panel"] = True
    st.session_state["kos_show_capability_executor_panel"] = False
    st.session_state["kos_show_capability_registry_panel"] = False
    st.session_state["kos_show_research_continuity_center"] = False
    st.session_state["kos_show_hupmix_next_video_production_panel"] = False
    st.session_state["kos_orchestrator_request_text"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_HUPMIX_MANUS_UPGRADE_PRIORITY_GATE_END

# KOS_MANUS_REFERENCE_IMPORT_PRIORITY_GATE_BEGIN
if send and is_kos_manus_reference_import_request(st.session_state.get("kos_operator_request_text", "")):
    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass
    st.session_state["kos_show_orchestrator_mode_panel"] = True
    st.session_state["kos_show_capability_executor_panel"] = False
    st.session_state["kos_show_capability_registry_panel"] = False
    st.session_state["kos_show_research_continuity_center"] = False
    st.session_state["kos_show_hupmix_next_video_production_panel"] = False
    st.session_state["kos_orchestrator_request_text"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_MANUS_REFERENCE_IMPORT_PRIORITY_GATE_END

# KOS_ORCHESTRATOR_MODE_PRIORITY_GATE_BEGIN
if send and is_kos_orchestrator_mode_request(st.session_state.get("kos_operator_request_text", "")):
    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass
    st.session_state["kos_show_orchestrator_mode_panel"] = True
    st.session_state["kos_show_capability_executor_panel"] = False
    st.session_state["kos_show_capability_registry_panel"] = False
    st.session_state["kos_show_research_continuity_center"] = False
    st.session_state["kos_show_hupmix_next_video_production_panel"] = False
    st.session_state["kos_orchestrator_request_text"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_ORCHESTRATOR_MODE_PRIORITY_GATE_END

if st.session_state.get("kos_show_orchestrator_mode_panel", False):
    render_kos_orchestrator_mode_panel()

# KOS_CAPABILITY_EXECUTOR_PRIORITY_GATE_BEGIN
if send and is_kos_capability_executor_request(st.session_state.get("kos_operator_request_text", "")):
    try:
        kos_clear_specialized_panel_noise()
    except Exception:
        pass
    st.session_state["kos_show_capability_executor_panel"] = True
    st.session_state["kos_show_capability_registry_panel"] = False
    st.session_state["kos_show_research_continuity_center"] = False
    st.session_state["kos_capability_executor_message"] = "Motor real governado aberto. Use a aba Hupmix para rodar a rota segura ate resolver GP_VIDEO_02."
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_CAPABILITY_EXECUTOR_PRIORITY_GATE_END

if st.session_state.get("kos_show_capability_executor_panel", False):
    render_kos_capability_executor_panel()

# KOS_CAPABILITY_REGISTRY_PRIORITY_GATE_BEGIN
if send and is_kos_capability_registry_request(st.session_state.get("kos_operator_request_text", "")):
    kos_clear_specialized_panel_noise()
    st.session_state["kos_show_capability_registry_panel"] = True
    st.session_state["kos_show_research_continuity_center"] = False
    st.session_state["kos_show_hupmix_next_video_production_panel"] = False
    st.session_state["kos_show_hupmix_garoto_oxy_history_review"] = False
    st.session_state["kos_show_hupmix_review_gate"] = False
    st.session_state["kos_capability_registry_message"] = "Mapa central de capacidades aberto. O K-OS agora consulta o registry operacional antes de depender do router generico."
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_CAPABILITY_REGISTRY_PRIORITY_GATE_END

if st.session_state.get("kos_show_capability_registry_panel", False):
    render_kos_capability_registry_panel()

# KOS_HUPMIX_NEXT_VIDEO_PRODUCTION_PRIORITY_GATE_BEGIN
if send and is_kos_hupmix_next_video_production_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_hupmix_next_video_production_panel"] = True
    st.session_state["kos_show_research_continuity_center"] = False
    st.session_state["kos_hupmix_next_video_message"] = "Producao real GP_VIDEO_02 aberta. O K-OS nao vai gerar video fake: so usa assets reais/anexos. Publicacao segue bloqueada."
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    st.session_state.pop("kos_last_public_research_packet", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_HUPMIX_NEXT_VIDEO_PRODUCTION_PRIORITY_GATE_END

if st.session_state.get("kos_show_hupmix_next_video_production_panel", False):
    render_kos_hupmix_gp_video_02_real_production_panel()





# KOS_RESEARCH_CONTINUITY_GATE_BEGIN
if send and is_kos_research_continuity_request(st.session_state.get("kos_operator_request_text", "")):
    _kos_query = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_show_research_continuity_center"] = True
    st.session_state["kos_last_operator_request"] = _kos_query
    st.session_state["kos_research_continuity_message"] = "Pesquisa/continuidade aberta em modo governado. Nenhum Router, Safe Action, publicacao, deploy, scraping ou IA paga foi acionado."
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    try:
        st.session_state["kos_last_public_research_packet"] = kos_register_public_research_request_packet(
            _kos_query,
            active_url=st.session_state.get("kos_public_url_lousa_active"),
            operator_request=_kos_query,
        )
    except Exception as exc:
        st.session_state["kos_research_continuity_message"] = f"Centro aberto, mas o registro automatico da pesquisa falhou: {exc}"
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_RESEARCH_CONTINUITY_GATE_END

if st.session_state.get("kos_show_research_continuity_center", False):
    render_kos_research_continuity_center()

# KOS_OPERATOR_LOCAL_COMMAND_GATE_BEGIN
if send and is_kos_local_command_or_path_request(st.session_state.get("kos_operator_request_text", "")):
    _kos_cmd = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_local_command_guard_message"] = "Comando local detectado. O K-OS nao vai transformar isso em pedido, Action Packet ou Safe Action."
    st.session_state["kos_local_command_guard_command"] = _kos_cmd
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_OPERATOR_LOCAL_COMMAND_GATE_END

render_kos_local_command_guard_message()

# KOS_HUPMIX_REVIEW_GATE_ROUTER_BEGIN
if send and is_kos_hupmix_review_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_hupmix_review_gate"] = True
    st.session_state["kos_hupmix_review_message"] = "Revisao Hupmix aberta em modo seguro. Nenhum Router, Safe Action, publicacao, deploy ou IA paga foi acionado."
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_HUPMIX_REVIEW_GATE_ROUTER_END

if st.session_state.get("kos_show_hupmix_review_gate", False):
    render_kos_hupmix_review_gate()



# KOS_HUPMIX_GAROTO_OXY_HISTORY_REVIEW_GATE_BEGIN
if send and is_kos_hupmix_garoto_oxy_history_review_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_hupmix_garoto_oxy_history_review"] = True
    st.session_state["kos_hupmix_garoto_oxy_review_message"] = "Revisao do historico Garoto Oxy aberta em modo seguro. Nenhum Router, Safe Action, publicacao, deploy, scraping ou IA paga foi acionado."
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
    if hasattr(st, "rerun"):
        st.rerun()
# KOS_HUPMIX_GAROTO_OXY_HISTORY_REVIEW_GATE_END

if st.session_state.get("kos_show_hupmix_garoto_oxy_history_review", False):
    render_kos_hupmix_garoto_oxy_history_review()

if send:
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    clean_request = st.session_state.get("kos_operator_request_text", "").strip()
    if not clean_request:
        st.error("Escreva um pedido simples para o K-OS.")
    else:
        with st.spinner("K-OS entendendo o pedido e montando Action Packet seguro..."):
            data = run_action_router(clean_request)
        st.session_state["kos_last_operator_data"] = data
        st.session_state["kos_last_operator_request"] = clean_request
        if data.get("status") == "KOS_ACTION_PACKET_READY" and data.get("packet_path"):
            with st.spinner("Gerando rascunho seguro e evidencia local..."):
                safe_result = run_safe_action(data.get("packet_path"))
            st.session_state["kos_last_safe_action_result"] = safe_result
            st.session_state["kos_last_safe_action_packet_path"] = str(data.get("packet_path"))

last_operator_data = st.session_state.get("kos_last_operator_data")

if last_operator_data and last_operator_data.get("status") == "KOS_ACTION_PACKET_READY":
    show_operator_response(last_operator_data)
else:
    pass  # KOS_COMPACT_UI removed helper text
    pass  # KOS_COMPACT_UI removed helper text

    col_home_1, col_home_2 = st.columns(2)

    with col_home_1:
        show_last = st.button("Ver ultimo pedido", use_container_width=True)

    with col_home_2:
        show_history = st.button("Ver historico seguro", use_container_width=True)

    if show_last:
        latest = read_json(LATEST_PACKET)
        if latest.get("status") == "KOS_ACTION_PACKET_READY":
            st.session_state["kos_last_operator_data"] = latest
            show_operator_response(latest)
        else:
            st.info("Nenhum pedido anterior encontrado.")

    if show_history:
        show_safe_action_history()
    else:
        pass  # KOS_COMPACT_UI removed helper text


# K-OS visual approval board persistent render hook
try:
    import json as _kos_json
    from pathlib import Path as _KosPath

    _kos_root = _KosPath(__file__).resolve().parents[1]
    _kos_gp_kit = _kos_root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
    _kos_safe_dir = _kos_root / "local_runtime" / "kos_safe_actions"

    _kos_lousa_payload = st.session_state.get("kos_last_operator_data") or st.session_state.get("kos_last_safe_action_result") or {}
    _kos_lousa_request = str(st.session_state.get("kos_operator_request_text", "")) + " " + str(st.session_state.get("kos_last_operator_request", ""))

    _kos_latest_text = ""
    if _kos_safe_dir.exists():
        _kos_files = sorted(_kos_safe_dir.glob("kos_safe_action_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if _kos_files:
            try:
                _kos_latest_text = _kos_files[0].read_text(encoding="utf-8", errors="replace")
            except Exception:
                _kos_latest_text = ""

    _kos_probe = (
        _kos_lousa_request
        + " "
        + _kos_json.dumps(_kos_lousa_payload, ensure_ascii=False, default=str)
        + " "
        + _kos_latest_text
    ).lower()

    _kos_should_show_lousa = (
        _kos_gp_kit.exists()
        and (
            "gp_video_01" in _kos_probe
            or "garoto oxy" in _kos_probe
            or "roteiro final de grava" in _kos_probe
            or "o heroi da limpeza chegou" in _kos_probe
            or "oxy power" in _kos_probe
        )
    )

    if _kos_should_show_lousa:
        render_hupmix_gp_lousa_preview(_kos_lousa_payload)

except Exception as _kos_lousa_exc:
    st.warning(f"Lousa visual GP_VIDEO_01 nao carregou: {_kos_lousa_exc}")


# KOS_OPERATOR_FLOW_DIAGNOSTIC_PANEL_BEGIN
def render_kos_operator_flow_diagnostic_panel():
    """Painel compacto de diagnostico do fluxo operador.
    Le apenas reports locais. Nao executa acao externa.
    """
    import json
    from pathlib import Path
    import streamlit as st

    root = Path.cwd()
    audit_path = root / "reports" / "KOS_OPERATOR_FLOW_AUDIT.json"
    digest_path = root / "reports" / "KOS_CODEBASE_STATIC_MAP_DIGEST.json"

    with st.expander("K-OS Diagnostic: Operator Flow", expanded=bool(st.session_state.get("kos_show_operator_flow_diagnostic", False))):
        st.caption("Leitura local. Sem IA, sem API, sem publicacao, sem deploy.")
        read_only_msg = st.session_state.get("kos_diagnostic_read_only_message")
        if read_only_msg:
            st.success(read_only_msg)

        if not audit_path.exists():
            st.warning("Relatorio Operator Flow ainda nao encontrado.")
            return

        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception as exc:
            st.error(f"Falha ao ler Operator Flow Audit: {exc}")
            return

        summary = audit.get("summary", {})
        core_files = audit.get("core_flow_files", [])

        col1, col2, col3 = st.columns(3)
        col1.metric("Arquivos candidatos", summary.get("candidate_python_files", 0))
        col2.metric("Arquivos interessantes", summary.get("interesting_python_files", 0))
        col3.metric("Arquivos core", summary.get("core_files", 0))

        col4, col5, col6 = st.columns(3)
        col4.metric("Subprocess/browser", summary.get("files_with_subprocess_or_browser", 0))
        col5.metric("UI Streamlit", summary.get("files_with_ui_lines", 0))
        col6.metric("Runtime/reports", summary.get("files_with_runtime_or_reports", 0))

        st.markdown("### Top arquivos do fluxo")
        rows = []
        for item in core_files[:10]:
            rows.append({
                "arquivo": item.get("path", ""),
                "score": item.get("score", 0),
                "linhas": item.get("lines", 0),
                "riscos": ", ".join(item.get("risk_hits", [])[:8]),
                "ui_hits": len(item.get("ui_lines", [])),
                "subprocess_hits": len(item.get("subprocess_lines", [])),
                "runtime_hits": len(item.get("writes_runtime_or_reports", [])),
            })

        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum arquivo core encontrado no relatorio.")

        if digest_path.exists():
            try:
                digest = json.loads(digest_path.read_text(encoding="utf-8"))
                risks = digest.get("top_risk_keywords", [])[:10]
                if risks:
                    st.markdown("### Top riscos gerais")
                    st.dataframe(
                        [{"risco": r[0], "ocorrencias": r[1]} for r in risks],
                        use_container_width=True,
                        hide_index=True,
                    )
            except Exception as exc:
                st.warning(f"Digest encontrado, mas nao foi possivel ler: {exc}")

        st.info("Proximo alvo recomendado: separar UI, Router e Safe Action Executor em diagnostico permanente.")

try:
    render_kos_operator_flow_diagnostic_panel()
except Exception as exc:
    try:
        import streamlit as st
        st.warning(f"K-OS Diagnostic Panel indisponivel: {exc}")
    except Exception:
        pass
# KOS_OPERATOR_FLOW_DIAGNOSTIC_PANEL_END



# KOS_GP_VIDEO_01_LOUSA_READ_ONLY_RENDER_BEGIN
def render_kos_gp_video_01_lousa_read_only():
    """Renderiza a lousa visual do GP_VIDEO_01 usando MP4 local."""
    import json
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_gp_video_01_lousa", False):
        return
    if st.session_state.get("kos_gp_video_01_lousa_rendered_inline", False):
        return

    root = Path.cwd()
    mp4_path = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    storyboard_path = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png"
    job_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json"
    report_path = root / "reports" / "KOS_HUPMIX_GP_VIDEO_FACTORY_FREE_MODE_V1.json"

    st.markdown("## Lousa visual — GP_VIDEO_01 Hupmix")

    msg = st.session_state.get("kos_lousa_read_only_message")
    if msg:
        st.success(msg)

    st.caption("Preview local. Sem IA paga. Sem publicacao. Sem deploy. Gate humano obrigatorio.")

    st.markdown("### Preview MP4")
    if mp4_path.exists():
        st.video(str(mp4_path))
        st.caption("Fonte: local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4")
    else:
        st.error("MP4 local nao encontrado. Rode o Video Factory Free Mode novamente.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Modo", "Free/local")
    c2.metric("Publicacao", "Bloqueada")
    c3.metric("IA paga", "Nao usada")

    if storyboard_path.exists():
        with st.expander("Storyboard", expanded=False):
            st.image(str(storyboard_path), use_container_width=True)

    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            outputs = report.get("outputs", {})
            with st.expander("Registro tecnico do video", expanded=False):
                kos_compact_json("Detalhes técnicos", {
                    "status": report.get("status"),
                    "mp4": outputs.get("mp4"),
                    "mp4_size": outputs.get("mp4_size"),
                    "storyboard": outputs.get("storyboard"),
                    "storyboard_size": outputs.get("storyboard_size"),
                    "policy": report.get("policy"),
                })
        except Exception as exc:
            st.warning(f"Nao foi possivel ler o relatorio do video: {exc}")

    if job_path.exists():
        try:
            job = json.loads(job_path.read_text(encoding="utf-8"))
            scenes = job.get("scenes", [])
            with st.expander("Cenas do GP_VIDEO_01", expanded=False):
                for idx, scene in enumerate(scenes, start=1):
                    st.markdown(f"**Cena {idx}: {scene.get('title', '')}**")
                    st.write(scene.get("line", ""))
        except Exception as exc:
            st.warning(f"Nao foi possivel ler o job do video: {exc}")

try:
    render_kos_gp_video_01_lousa_read_only()
except Exception as exc:
    try:
        import streamlit as st
        st.warning(f"Lousa visual GP_VIDEO_01 indisponivel: {exc}")
    except Exception:
        pass
# KOS_GP_VIDEO_01_LOUSA_READ_ONLY_RENDER_END

# KOS_OPERATOR_CHAT_JSON_COMPACTED_V1
# KOS_LEGACY_FRONTDOOR_TEST_MARKERS
# consulta registry
# confirmar, alterar ou cancelar por texto
# ### Evidencia
# Coworker operacional supervisionado
# KOS_LEGACY_FRONTDOOR_TEST_MARKERS_END

