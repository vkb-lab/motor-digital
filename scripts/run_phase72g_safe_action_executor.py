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
    return {
        "title": "Diagnostico seguro de agentes",
        "summary": "Checklist operacional criado. Nenhum agente executou acao externa.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Verificacoes sugeridas", "items": [
                "Fila de missoes pendentes.",
                "Eventos recentes de runtime.",
                "Pacotes aguardando gate humano.",
                "Modulos com erro ou sem ultimo status.",
                "Acoes externas bloqueadas."
            ]},
            {"title": "Atencao principal", "items": [
                "Priorizar apenas missoes com baixo risco.",
                "Nao executar publicacao, patch ou deploy sem confirmacao humana."
            ]},
        ],
    }


def build_patches(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Proposta segura de patch",
        "summary": "Plano de correcao criado para revisao. Nenhum patch foi aplicado automaticamente.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Fluxo seguro", "items": [
                "Verificar Git limpo.",
                "Gerar proposta de patch.",
                "Mostrar diff.",
                "Aguardar aprovacao humana.",
                "Commit somente apos validacao."
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