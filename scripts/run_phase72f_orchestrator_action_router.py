from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "local_runtime" / "kos_action_router"
MEMORY_DIR = ROOT / "memory" / "kos_action_router"`nLATEST_PACKET = RUNTIME_DIR / "latest_action_packet.json"`nEVENTS = RUNTIME_DIR / "events.jsonl"

LOCKS = {
    "auto_publish_enabled": False,
    "auto_execution_enabled": False,
    "paid_ai_enabled": False,
    "parada_atlantida_locked": True,
    "browser_logged_automation_blocked": True,
    "human_gate_required": True,
}

ROUTES = {
    "social_publish": {
        "label": "Redes sociais / Hupmix / campanhas",
        "modules": [
            "71A Social Ops Control Center",
            "71B Social Strategy Generator",
            "71C Social Publish Readiness Auditor",
            "69F/69G/69H Publish Gates"
        ],
        "next_step": "Preparar plano de campanha em rascunho e revisar antes de qualquer acao real.",
        "risk": "Publicacao automatica bloqueada. Instagram real exige confirmacao humana explicita.",
        "safe_action": "Gerar plano operacional de campanha sem publicar.",
        "internal_commands": [
            "python scripts\\run_phase71b_social_strategy_generator.py --target hupmix --objective \"<objetivo>\" --campaign hupmix-weekly",
            "python scripts\\run_phase71c_social_publish_readiness_auditor.py --target hupmix --asset-url \"<asset>\" --caption \"<legenda>\""
        ],
    },
    "products_saas": {
        "label": "Produto SaaS / MVP / landing",
        "modules": [
            "Product Factory",
            "SaaS Product Mission Pack",
            "Mission Planner",
            "Human Decision Center"
        ],
        "next_step": "Criar escopo pequeno de MVP, com nome, publico, promessa, tela inicial e proxima entrega.",
        "risk": "Sem deploy automatico e sem gasto externo sem gate humano.",
        "safe_action": "Gerar blueprint de produto SaaS em rascunho.",
        "internal_commands": [
            "python scripts\\run_product_factory.py --mode draft",
            "python scripts\\run_saas_product_mission_pack.py --mode draft"
        ],
    },
    "agents_orchestration": {
        "label": "Agentes / orquestrador / missoes",
        "modules": [
            "Mission Queue",
            "Mission Planner",
            "Mission Executor Bridge",
            "Handoff / Queue",
            "Runtime Control"
        ],
        "next_step": "Verificar fila, status de agentes e pontos que precisam de atencao.",
        "risk": "Execucao automatica perigosa bloqueada. Acoes reais exigem revisao.",
        "safe_action": "Gerar diagnostico operacional dos agentes.",
        "internal_commands": [
            "python scripts\\run_mission_queue_status.py",
            "python scripts\\run_runtime_control_status.py"
        ],
    },
    "patches": {
        "label": "Codigo / correcoes / melhorias",
        "modules": [
            "70A Safe Patch Proposer",
            "70B Safe Patch Review Panel",
            "Git Safety Gate",
            "Patch Review"
        ],
        "next_step": "Gerar proposta de patch revisavel, sem aplicar automaticamente.",
        "risk": "Patch automatico bloqueado. Git sujo bloqueia alteracoes.",
        "safe_action": "Criar proposta de patch para revisao humana.",
        "internal_commands": [
            "python scripts\\run_phase70a_safe_patch_proposer.py --request \"<pedido>\""
        ],
    },
    "runtime_bridge": {
        "label": "Runtime / ponte ChatGPT / logs",
        "modules": [
            "70C ChatGPT Conversation Bridge",
            "70D Drop Watcher",
            "70E Runtime Controller",
            "Runtime Control"
        ],
        "next_step": "Verificar status da ponte local, arquivos recentes e eventos pendentes.",
        "risk": "Sem scraping, sem cookies e sem automacao de navegador logado.",
        "safe_action": "Gerar status da ponte local e pendencias.",
        "internal_commands": [
            "python scripts\\run_chatgpt_bridge_runtime_status.py"
        ],
    },
    "admin": {
        "label": "Administracao / rotina / organizacao",
        "modules": [
            "72A Weekly Operator Workspace",
            "Unified Command Cockpit",
            "Human Decision Center",
            "Reports"
        ],
        "next_step": "Organizar prioridades, pendencias e proxima acao simples.",
        "risk": "Nenhuma acao externa automatica sera executada.",
        "safe_action": "Gerar resumo operacional e lista curta de prioridades.",
        "internal_commands": [
            "python scripts\\run_weekly_operator_workspace.py --mode summary"
        ],
    },
    "general": {
        "label": "Geral",
        "modules": [
            "K-OS Orchestrator",
            "Human Decision Center",
            "Runtime Control"
        ],
        "next_step": "Transformar o pedido em plano simples antes de executar.",
        "risk": "Acoes reais permanecem bloqueadas ate confirmacao humana.",
        "safe_action": "Gerar plano operacional simples.",
        "internal_commands": []
    }
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def call_72c(request: str) -> dict:
    script = ROOT / "scripts" / "run_phase72c_orchestrator_request_box.py"
    if not script.exists():
        return {"status": "MISSING_72C", "route": "general"}

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--request", request],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
    except Exception as exc:
        return {"status": "72C_CALL_ERROR", "route": "general", "error": str(exc)}

    stdout = (result.stdout or "").strip()
    try:
        data = json.loads(stdout)
        data["returncode"] = result.returncode
        return data
    except Exception:
        latest = ROOT / "local_runtime" / "kos_orchestrator_request_box" / "latest_orchestrator_response.json"
        if latest.exists():
            try:
                data = json.loads(latest.read_text(encoding="utf-8-sig"))
                data["returncode"] = result.returncode
                return data
            except Exception:
                pass

    return {
        "status": "72C_OUTPUT_NOT_JSON",
        "route": "general",
        "stdout_tail": stdout[-1000:],
        "stderr_tail": (result.stderr or "")[-1000:],
        "returncode": result.returncode,
    }


def detect_route(request: str, base: dict) -> str:
    text = normalize(request)
    base_route = base.get("route")
    if base_route in ROUTES:
        return base_route

    social_words = ["hupmix", "instagram", "campanha", "post", "reels", "story", "stories", "publicar", "social"]
    product_words = ["saas", "produto", "mvp", "landing", "app", "startup", "projeto"]
    agent_words = ["agente", "agentes", "status", "fila", "missao", "missao", "orquestrador", "atenção", "atencao"]
    patch_words = ["corrigir", "bug", "patch", "codigo", "código", "arquivo", "implementar"]
    runtime_words = ["bridge", "chatgpt", "runtime", "watcher", "log", "porta", "streamlit"]
    admin_words = ["rotina", "prioridade", "organizar", "agenda", "semana", "admin"]

    if any(w in text for w in social_words):
        return "social_publish"
    if any(w in text for w in product_words):
        return "products_saas"
    if any(w in text for w in agent_words):
        return "agents_orchestration"
    if any(w in text for w in patch_words):
        return "patches"
    if any(w in text for w in runtime_words):
        return "runtime_bridge"
    if any(w in text for w in admin_words):
        return "admin"
    return "general"


def summarize_request(request: str, route: str) -> str:
    clean = " ".join((request or "").split())
    if clean:
        return clean[:240]

    if route == "social_publish":
        return "Pedido de campanha ou redes sociais recebido."
    if route == "products_saas":
        return "Pedido de criacao de produto SaaS recebido."
    if route == "agents_orchestration":
        return "Pedido de status ou coordenacao de agentes recebido."
    return "Pedido recebido pelo K-OS."


def build_packet(request: str) -> dict:
    base = call_72c(request)
    route = detect_route(request, base)
    spec = ROUTES.get(route, ROUTES["general"])
    packet_id = "kos_action_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]

    packet = {
        "status": "KOS_ACTION_PACKET_READY",
        "packet_id": packet_id,
        "created_at": now_iso(),
        "request": request,
        "route": route,
        "route_label": spec["label"],
        "operator_response": {
            "entendi": summarize_request(request, route),
            "vou_usar_estes_modulos": spec["modules"],
            "proximo_passo": spec["next_step"],
            "risco_bloqueio": spec["risk"],
            "acao_segura_disponivel": spec["safe_action"],
        },
        "action_packet": {
            "route": route,
            "intent_summary": summarize_request(request, route),
            "modules": spec["modules"],
            "safe_action": spec["safe_action"],
            "requires_human_gate": True,
            "allowed_now": [
                "draft_plan",
                "readiness_check",
                "status_check",
                "proposal_only"
            ],
            "blocked_now": [
                "auto_publish",
                "paid_ai_call",
                "logged_browser_automation",
                "cookie_access",
                "automatic_patch_apply",
                "parada_atlantida_execution"
            ],
            "internal_commands_hidden_by_default": spec["internal_commands"],
        },
        "locks": LOCKS,
        "source_72c": {
            "status": base.get("status"),
            "route": base.get("route"),
            "returncode": base.get("returncode"),
        },
    }
    return packet


def save_packet(packet: dict) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)`n    packet_path = RUNTIME_DIR / f"{packet['packet_id']}.json"
    packet["packet_path"] = str(packet_path)

    payload = json.dumps(packet, ensure_ascii=False, indent=2)
    packet_path.write_text(payload, encoding="utf-8")
    LATEST_PACKET.write_text(payload, encoding="utf-8")

    event = {
        "ts": now_iso(),
        "event": "kos_action_packet_created",
        "packet_id": packet["packet_id"],
        "route": packet["route"],
        "status": packet["status"],
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()

    packet = build_packet(args.request)
    save_packet(packet)

    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())