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


def build_social(packet: dict) -> dict:
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


BUILDERS = {
    "social_publish": build_social,
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