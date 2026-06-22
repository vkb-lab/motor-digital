from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
ACTION_ROUTER_DIR = ROOT / "local_runtime" / "kos_action_router"
LATEST_PACKET = ACTION_ROUTER_DIR / "latest_action_packet.json"
SAFE_DIR = ROOT / "local_runtime" / "kos_safe_actions"
LATEST_SAFE_ACTION = SAFE_DIR / "latest_safe_action.json"
EVENTS = SAFE_DIR / "events.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc), "path": str(path)}


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def as_lines(items: list[str]) -> str:
    return "\n".join("- " + item for item in items)



def kos_is_social_read_request(value: str) -> bool:
    table = str.maketrans({
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
        "Á": "a", "À": "a", "Â": "a", "Ã": "a",
        "É": "e", "Ê": "e",
        "Í": "i",
        "Ó": "o", "Ô": "o", "Õ": "o",
        "Ú": "u",
        "Ç": "c",
    })
    text = str(value or "").lower().translate(table)
    social_markers = ["hupmix", "instagram", "post", "publicacao", "publicacoes", "reels", "story", "stories", "perfil"]
    read_markers = ["veja", "ver", "olhar", "olhe", "ultima", "ultimo", "analisar", "analise", "avaliar", "auditar", "revisar", "ler", "leia"]
    return any(word in text for word in social_markers) and any(word in text for word in read_markers)


def build_social_read(packet: dict) -> dict:
    request = packet.get("request", "")

    def clip(value, limit=900):
        value = str(value or "")
        if len(value) <= limit:
            return value
        return value[:limit].rstrip() + "..."

    def safe_number(value):
        if value is None:
            return "nao informado"
        return str(value)

    def fallback(reason, detail=""):
        items = [
            "O K-OS tentou usar o conector oficial Meta/Instagram em modo read-only.",
            "Nenhum navegador logado foi usado.",
            "Nenhum scraping foi usado.",
            "Nenhuma publicacao foi executada.",
            "Motivo: " + str(reason),
        ]
        if detail:
            items.append("Detalhe tecnico resumido: " + clip(detail, 500))

        return {
            "title": "Analise oficial de publicacao Hupmix",
            "summary": "Conector oficial nao completou a leitura. Nenhuma acao externa foi executada.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Status", "items": items},
                {"title": "Proxima acao segura", "items": [
                    "Verificar token Meta, permissao do app ou relatorio local.",
                    "Nao publicar nada ate nova validacao."
                ]},
            ],
        }

    audit_script = ROOT / "scripts" / "run_phase69d_hupmix_instagram_audit.py"
    audit_report = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix" / "latest_hupmix_instagram_audit.json"

    if not audit_script.exists():
        return fallback("script oficial de auditoria Hupmix nao encontrado")

    try:
        subprocess = __import__("subprocess")
        sysmod = __import__("sys")
        completed = subprocess.run(
            [sysmod.executable, str(audit_script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
    except Exception as exc:
        return fallback("erro ao chamar auditoria oficial", str(exc))

    if not audit_report.exists():
        return fallback("relatorio oficial de auditoria nao encontrado", completed.stderr or completed.stdout)

    audit = read_json(audit_report)

    if audit.get("status") != "KOS_HUPMIX_INSTAGRAM_AUDIT_CONNECTED":
        return fallback(
            audit.get("status", "auditoria nao conectada"),
            json.dumps(audit.get("graph_error", audit), ensure_ascii=False)[:900],
        )

    media_items = audit.get("recent_media_summary", []) or []
    latest = media_items[0] if media_items else {}

    caption = latest.get("caption_preview", "")
    caption_lower = caption.lower()
    first_line = caption.splitlines()[0].strip() if caption else "Sem legenda disponivel na amostra."
    likes = latest.get("like_count")
    comments = latest.get("comments_count")

    strengths = []
    risks = []
    suggestions = []

    if "r$" in caption_lower or "por apenas" in caption_lower:
        strengths.append("Oferta/preco aparece de forma clara na legenda.")
    if "passe na" in caption_lower or "direct" in caption_lower or "chame" in caption_lower:
        strengths.append("Existe chamada para acao ou direcao de contato.")
    if "sem cloro" in caption_lower or "nao toxico" in caption_lower or "limpa tudo" in caption_lower:
        strengths.append("Beneficios do produto aparecem de forma objetiva.")

    if not strengths:
        strengths.append("A publicacao possui conteudo suficiente para analise inicial.")

    if likes is not None and comments is not None and int(comments or 0) == 0:
        risks.append("Comentarios zerados indicam baixa conversa publica no post.")
    if len(caption) > 700:
        risks.append("Legenda longa. Pode precisar de gancho mais direto nos primeiros segundos.")
    if not risks:
        risks.append("Nenhum risco critico identificado na leitura resumida.")

    suggestions.append("Reforcar o gancho inicial com dor + promessa em uma frase curta.")
    suggestions.append("Adicionar CTA mais direto para WhatsApp, direct ou visita na loja.")
    suggestions.append("Transformar esta leitura em proximo post, story ou oferta da semana somente apos revisao humana.")

    latest_items = []
    if latest:
        latest_items = [
            "Tipo: " + str(latest.get("media_type", "nao informado")),
            "Data: " + str(latest.get("timestamp", "nao informado")),
            "Link: " + str(latest.get("permalink", "nao informado")),
            "Curtidas: " + safe_number(likes),
            "Comentarios: " + safe_number(comments),
            "Gancho inicial: " + clip(first_line, 280),
            "Legenda resumida: " + clip(caption, 900),
        ]
    else:
        latest_items = ["Nenhuma midia recente retornada pela auditoria oficial."]

    return {
        "title": "Analise oficial da ultima publicacao Hupmix",
        "summary": "Leitura feita via Meta Graph API oficial. Nenhum navegador, scraping ou publicacao foi usado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Fonte oficial usada", "items": [
                "Meta Graph API oficial.",
                "Conta: @" + str(audit.get("username", "hupmix")),
                "IG ID: " + str(audit.get("ig_id", "")),
                "Midias totais no perfil: " + safe_number(audit.get("media_count")),
                "Publicacao executada: nao.",
                "Navegador logado usado: nao.",
                "Scraping usado: nao.",
            ]},
            {"title": "Ultima publicacao encontrada", "items": latest_items},
            {"title": "Pontos fortes", "items": strengths},
            {"title": "Pontos de atencao", "items": risks},
            {"title": "Sugestoes de melhoria", "items": suggestions},
            {"title": "Proxima acao segura", "items": [
                "Gerar sugestao de legenda revisada em rascunho.",
                "Criar plano de stories de apoio sem publicar automaticamente.",
                "Manter publicacao real bloqueada ate gate humano explicito."
            ]},
        ],
    }



def build_hupmix_gp_continuity(packet: dict) -> dict:
    request = packet.get("request", "")

    package_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json"
    markdown_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.md"

    def clip(value, limit=700):
        value = str(value or "")
        if len(value) <= limit:
            return value
        return value[:limit].rstrip() + "..."

    if not package_path.exists():
        return {
            "title": "Continuidade GP Hupmix",
            "summary": "Pacote GP ainda nao encontrado. Nenhuma acao real foi executada.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Proxima acao segura", "items": [
                    "Gerar novamente o pacote de continuidade GP Hupmix.",
                    "Nao publicar nada ate o pacote ser recuperado."
                ]},
            ],
        }

    package = json.loads(package_path.read_text(encoding="utf-8"))

    videos = package.get("videos", []) or []
    stories = package.get("stories", []) or []
    calendar = package.get("calendar_7_days", []) or []
    approval = package.get("approval_gate", []) or []
    source = package.get("source", {}) or {}
    safety = package.get("safety", {}) or {}

    video_items = []
    for video in videos:
        video_items.append(
            str(video.get("id", "VIDEO")) + " - " +
            str(video.get("title", "Sem titulo")) +
            " | Formato: " + str(video.get("format", "nao informado")) +
            " | Gancho: " + clip(video.get("hook", ""), 180) +
            " | CTA: " + clip(video.get("cta", ""), 160)
        )

    first_video = videos[0] if videos else {}
    first_script = first_video.get("script", []) or []

    return {
        "title": "Continuidade oficial da campanha GP Hupmix",
        "summary": "Pacote de continuidade recuperado do repositorio. Nenhuma publicacao foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Campanha recuperada", "items": [
                "Marca: " + str(package.get("brand", "Hupmix")),
                "Campanha: " + str(package.get("campaign", "GP / Garoto Oxy Power / Oxy Power")),
                "Status: " + str(package.get("status", "pacote recuperado")),
                "Base Instagram: " + str(source.get("latest_permalink", "nao informado")),
                "Arquivos locais relacionados na auditoria: " + str(source.get("local_matches_count", "nao informado")),
            ]},
            {"title": "Proximos videos planejados", "items": video_items or ["Nenhum video planejado encontrado no pacote."]},
            {"title": "Proximo video recomendado", "items": [
                "ID: " + str(first_video.get("id", "nao informado")),
                "Titulo: " + str(first_video.get("title", "nao informado")),
                "Formato: " + str(first_video.get("format", "nao informado")),
                "Gancho: " + str(first_video.get("hook", "nao informado")),
                "Legenda base: " + clip(first_video.get("caption", "nao informado"), 500),
                "CTA: " + str(first_video.get("cta", "nao informado")),
            ]},
            {"title": "Roteiro do proximo video", "items": first_script or ["Roteiro nao encontrado."]},
            {"title": "Stories de apoio", "items": stories or ["Nenhum story planejado encontrado."]},
            {"title": "Calendario de 7 dias", "items": calendar or ["Calendario nao encontrado."]},
            {"title": "Gate humano obrigatorio", "items": approval or [
                "Revisar preco.",
                "Confirmar estoque.",
                "Aprovar manualmente antes de qualquer publicacao real."
            ]},
            {"title": "Seguranca operacional", "items": [
                "Publicacao executada: " + str(bool(safety.get("instagram_publish_executed", False))).lower(),
                "Navegador logado usado: " + str(bool(safety.get("browser_logged_account_automation_used", False))).lower(),
                "Scraping usado: " + str(bool(safety.get("scraping_used", False))).lower(),
                "Gate humano requerido: " + str(bool(safety.get("human_gate_required", True))).lower(),
                "Arquivo base: " + str(markdown_path),
            ]},
            {"title": "Proxima acao segura", "items": [
                "Gerar versao final do roteiro GP_VIDEO_01 para gravacao.",
                "Gerar lista de cenas e falas do Garoto Oxy.",
                "Gerar legenda final em rascunho.",
                "Nao publicar sem aprovacao humana explicita."
            ]},
        ],
    }



def build_social(packet: dict) -> dict:
    request_text = str(packet.get("request", "")).lower()
    if "hupmix" in request_text and ("gp" in request_text or "garoto" in request_text or "oxy" in request_text):
        return build_hupmix_gp_continuity(packet)

    if kos_is_social_read_request(packet.get("request", "")):
        return build_social_read(packet)
    request = packet.get("request", "")
    days = [
        "Dia 1: promessa principal da Hupmix e chamada para conhecer a marca.",
        "Dia 2: dor do cliente e como a Hupmix resolve de forma simples.",
        "Dia 3: prova social ou bastidor leve.",
        "Dia 4: oferta educativa sem venda agressiva.",
        "Dia 5: comparativo antes/depois ou checklist.",
        "Dia 6: chamada para conversa ou direct.",
        "Dia 7: resumo da semana e convite para proximo passo."
    ]
    return {
        "title": "Rascunho seguro de campanha Hupmix",
        "summary": "Plano de 7 dias criado em modo rascunho. Nenhuma publicacao foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Plano de 7 dias", "items": days},
            {"title": "Proximo passo humano", "items": ["Revisar tema, imagens e legenda antes de qualquer publicacao."]},
            {"title": "Bloqueios preservados", "items": ["Publicacao automatica bloqueada.", "Instagram real exige confirmacao humana."]},
        ],
    }


def build_saas(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Blueprint seguro de MVP SaaS",
        "summary": "Escopo inicial de produto criado em modo rascunho. Nenhum deploy ou gasto externo foi executado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Nome de trabalho", "items": ["K-OS Mini SaaS Pilot"]},
            {"title": "Publico inicial", "items": ["Pequenos negocios que precisam organizar operacao, campanhas e tarefas com baixa complexidade."]},
            {"title": "Promessa simples", "items": ["Transformar pedidos soltos em plano operacional claro, com proximas acoes seguras."]},
            {"title": "Primeira tela", "items": ["Uma caixa de pedido.", "Resumo do entendimento.", "Proximo passo seguro.", "Registro de bloqueios."]},
            {"title": "Entrega desta semana", "items": ["Blueprint do MVP.", "Uma tela Streamlit simples.", "Um JSON de estado do produto.", "Sem deploy automatico."]},
        ],
    }


def build_agents(packet: dict) -> dict:
    request = packet.get("request", "")

    def mtime_label(path: Path) -> str:
        try:
            return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "sem data"

    def compact_value(value):
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, list):
            return str(len(value)) + " item(ns)"
        if isinstance(value, dict):
            return str(len(value)) + " chave(s)"
        if value is None:
            return "vazio"
        return type(value).__name__

    def extract_signals(data) -> str:
        if not isinstance(data, dict):
            return "conteudo lido"

        preferred = [
            "status", "state", "ok", "health", "mode", "last_status",
            "queue_status", "runner_status", "processor_status",
            "pending_count", "processed_count", "error_count",
            "last_error", "updated_at", "created_at", "generated_at",
            "last_tick_at", "timestamp"
        ]

        signals = []
        for key in preferred:
            if key in data and data.get(key) not in [None, "", [], {}]:
                signals.append(str(key) + "=" + compact_value(data.get(key)))

        if len(signals) < 4:
            for key, value in data.items():
                low = str(key).lower()
                if any(token in low for token in ["queue", "mission", "job", "task", "action", "decision", "pending", "error"]):
                    if value not in [None, "", [], {}]:
                        item = str(key) + "=" + compact_value(value)
                        if item not in signals:
                            signals.append(item)
                if len(signals) >= 6:
                    break

        if not signals:
            signals.append("arquivo lido, sem sinal operacional explicito")

        return "; ".join(signals[:6])

    def summarize_json_file(label: str, path: Path) -> str:
        if not path.exists():
            return label + ": nao encontrado"

        data = read_json(path)
        if isinstance(data, dict) and data.get("status") == "READ_ERROR":
            return label + ": erro de leitura - " + str(data.get("error", "sem detalhe"))

        status = "lido"
        if isinstance(data, dict) and data.get("status"):
            status = str(data.get("status"))

        return label + ": " + status + "; atualizado em " + mtime_label(path) + "; " + extract_signals(data)

    def summarize_decision_queue(path: Path) -> str:
        if not path.exists():
            return "Fila de decisao humana: nao encontrada"

        data = read_json(path)
        if isinstance(data, dict) and data.get("status") == "READ_ERROR":
            return "Fila de decisao humana: erro de leitura - " + str(data.get("error", "sem detalhe"))

        count = None
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            for key in ["queue", "items", "decisions", "pending", "requests", "tasks"]:
                if isinstance(data.get(key), list):
                    count = len(data.get(key))
                    break
            if count is None:
                count = len(data.keys())

        if count is None:
            return "Fila de decisao humana: arquivo lido; atualizado em " + mtime_label(path)

        return "Fila de decisao humana: " + str(count) + " registro(s); atualizado em " + mtime_label(path)

    def summarize_jsonl_events(label: str, path: Path, limit: int = 5) -> list:
        if not path.exists():
            return [label + ": nao encontrado"]

        try:
            rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except Exception as exc:
            return [label + ": erro de leitura - " + str(exc)]

        if not rows:
            return [label + ": sem eventos registrados"]

        out = []
        for raw in rows[-limit:]:
            try:
                event = json.loads(raw)
                if isinstance(event, dict):
                    bits = []
                    for key in ["event", "status", "route", "action_id", "packet_id", "created_at", "timestamp"]:
                        if event.get(key) not in [None, "", [], {}]:
                            bits.append(str(key) + "=" + str(event.get(key)))
                    out.append("; ".join(bits[:6]) if bits else "evento lido")
                else:
                    out.append("evento lido")
            except Exception:
                out.append(raw[:160])

        return out

    runtime_items = [
        summarize_json_file(
            "Fila de missoes",
            ROOT / "local_runtime" / "kos_autonomy_missions" / "latest_queue_processor_status.json"
        ),
        summarize_json_file(
            "Tick da fila de missoes",
            ROOT / "local_runtime" / "kos_autonomy_missions" / "latest_mission_queue_loop_tick.json"
        ),
        summarize_json_file(
            "Runner de jobs autonomos",
            ROOT / "local_runtime" / "kos_autonomous_jobs" / "latest_autonomous_job_runner_status.json"
        ),
        summarize_json_file(
            "Tick do runner autonomo",
            ROOT / "local_runtime" / "kos_autonomous_jobs" / "latest_autonomous_job_runner_loop_tick.json"
        ),
        summarize_json_file(
            "Ultimo Action Packet",
            ROOT / "local_runtime" / "kos_action_router" / "latest_action_packet.json"
        ),
        summarize_json_file(
            "Ultima acao segura",
            ROOT / "local_runtime" / "kos_safe_actions" / "latest_safe_action.json"
        ),
        summarize_decision_queue(
            ROOT / "live" / "human_decision_center" / "decision_queue.json"
        ),
    ]

    event_items = []
    event_items.extend(summarize_jsonl_events(
        "Eventos do roteador",
        ROOT / "local_runtime" / "kos_action_router" / "events.jsonl",
        limit=3
    ))
    event_items.extend(summarize_jsonl_events(
        "Eventos de acoes seguras",
        ROOT / "local_runtime" / "kos_safe_actions" / "events.jsonl",
        limit=3
    ))

    attention = []
    joined = "\n".join(runtime_items + event_items).lower()

    if "erro" in joined or "read_error" in joined or "failed" in joined or "failure" in joined:
        attention.append("Existe sinal de erro ou falha nos registros. Revisar antes de executar qualquer acao real.")
    else:
        attention.append("Nenhum erro critico foi identificado na leitura resumida dos arquivos monitorados.")

    if "nao encontrado" in joined:
        attention.append("Alguns arquivos de runtime nao foram encontrados. Isso pode ser normal se o modulo ainda nao rodou.")
    else:
        attention.append("Arquivos principais de runtime foram encontrados.")

    attention.append("Manter publicacao, patch e deploy bloqueados ate aprovacao humana.")

    return {
        "title": "Diagnostico operacional real de agentes",
        "summary": "Estado real lido de local_runtime e live. Nenhum agente executou acao externa.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resumo simples", "items": [
                "Leitura feita em arquivos locais de runtime, fila, jobs, Action Packets, acoes seguras e decisao humana.",
                "Este diagnostico apenas le dados. Nao executa agente, nao publica, nao aplica patch e nao faz deploy."
            ]},
            {"title": "Estado real encontrado", "items": runtime_items},
            {"title": "Ultimos eventos", "items": event_items},
            {"title": "Atencao necessaria", "items": attention},
            {"title": "Proxima acao segura", "items": [
                "Revisar somente itens com erro, pendencia ou arquivo ausente.",
                "Executar acoes reais apenas com gate humano explicito."
            ]},
        ],
    }


def build_runtime(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Status seguro de runtime",
        "summary": "Plano de verificacao de runtime criado sem mexer em navegador, cookies ou sessao logada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Itens de status", "items": [
                "Porta principal do K-OS.",
                "Processo Streamlit ativo.",
                "Ultimo Action Packet.",
                "Eventos locais recentes.",
                "Bloqueios ativos."
            ]},
        ],
    }


def build_admin(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Resumo administrativo seguro",
        "summary": "Plano curto de organizacao criado sem executar acao externa.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Prioridades", "items": [
                "Manter entrada unica do K-OS.",
                "Reduzir comandos manuais.",
                "Executar apenas acoes seguras por botao.",
                "Registrar decisoes com gate humano."
            ]},
        ],
    }


def build_general(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Plano operacional seguro",
        "summary": "Pedido transformado em plano simples. Nenhuma acao real foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Proximo passo", "items": ["Refinar o pedido ou escolher uma acao segura dentro do K-OS."]},
        ],
    }



def build_patches(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Plano seguro de patch",
        "summary": "Plano de patch criado em rascunho. Nenhum arquivo foi alterado automaticamente.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resumo simples", "items": [
                "O K-OS preparou apenas um rascunho seguro.",
                "Nenhum deploy, patch, publicacao ou acao externa foi executado."
            ]},
            {"title": "Atencao necessaria", "items": [
                "Patch automatico bloqueado. Revisar diff e aprovar manualmente antes de aplicar.",
                "Gate humano obrigatorio preservado."
            ]},
            {"title": "Proxima acao segura", "items": [
                "Gerar proposta de patch revisavel, sem aplicar automaticamente."
            ]},
        ],
    }

BUILDERS = {
    "social_publish": build_social,
    "social_read": build_social_read,
    "products_saas": build_saas,
    "agents_orchestration": build_agents,
    "patches": build_patches,
    "runtime_bridge": build_runtime,
    "admin": build_admin,
    "general": build_general,
}


def render_markdown(result: dict) -> str:
    lines = [
        "# " + result["title"],
        "",
        result["summary"],
        "",
    ]
    for section in result.get("sections", []):
        lines.append("## " + section.get("title", "Secao"))
        lines.append("")
        lines.append(as_lines([str(x) for x in section.get("items", [])]))
        lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- Sem publicacao automatica.")
    lines.append("- Sem deploy automatico.")
    lines.append("- Sem patch automatico.")
    lines.append("- Sem IA paga.")
    lines.append("- Sem automacao de navegador logado.")
    lines.append("- Gate humano obrigatorio para acoes reais.")
    lines.append("")
    return "\n".join(lines)


def execute_safe_action(packet: dict) -> dict:
    SAFE_DIR.mkdir(parents=True, exist_ok=True)

    route = packet.get("route", "general")
    builder = BUILDERS.get(route, build_general)
    result = builder(packet)

    action_id = "kos_safe_action_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    md_path = SAFE_DIR / f"{action_id}.md"
    json_path = SAFE_DIR / f"{action_id}.json"

    payload = {
        "status": "KOS_SAFE_ACTION_READY",
        "action_id": action_id,
        "created_at": now_iso(),
        "source_packet_id": packet.get("packet_id"),
        "route": route,
        "route_label": packet.get("route_label"),
        "title": result["title"],
        "summary": result["summary"],
        "sections": result.get("sections", []),
        "guardrails": {
            "auto_publish": "blocked",
            "auto_deploy": "blocked",
            "auto_patch": "blocked",
            "paid_ai": "blocked",
            "logged_browser_automation": "blocked",
            "human_gate_required": True,
        },
        "files": {
            "json": str(json_path),
            "markdown": str(md_path),
        },
    }

    md_path.write_text(render_markdown(result), encoding="utf-8")
    write_json(json_path, payload)
    write_json(LATEST_SAFE_ACTION, payload)

    event = {
        "ts": now_iso(),
        "event": "kos_safe_action_created",
        "action_id": action_id,
        "route": route,
        "source_packet_id": packet.get("packet_id"),
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-path", default="")
    parser.add_argument("--latest", action="store_true")
    args = parser.parse_args()

    if args.packet_path:
        packet_path = Path(args.packet_path)
    else:
        packet_path = LATEST_PACKET

    packet = read_json(packet_path)
    if packet.get("status") != "KOS_ACTION_PACKET_READY":
        print(json.dumps({
            "status": "NO_VALID_ACTION_PACKET",
            "packet_path": str(packet_path),
            "packet_status": packet.get("status"),
        }, ensure_ascii=False, indent=2))
        return 1

    result = execute_safe_action(packet)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
