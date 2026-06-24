from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

INBOX = ROOT / "local_runtime" / "kos_orchestrator_request_box" / "inbox"
RESPONSES = ROOT / "local_runtime" / "kos_orchestrator_request_box" / "responses"
LATEST_RESPONSE = ROOT / "local_runtime" / "kos_orchestrator_request_box" / "latest_orchestrator_response.json"
LATEST_INVENTORY = ROOT / "local_runtime" / "kos_unified_cockpit" / "latest_inventory.json"

SAFE_FLAGS = {
    "auto_publish_enabled": False,
    "auto_execution_enabled": False,
    "operator_review_required": True,
    "human_confirmation_required": True,
    "parada_atlantida_locked": True,
    "target_test_account": "registry_resolved",
    "paid_ai_locked": True,
    "browser_scraping_enabled": False,
    "browser_logged_account_automation_used": False,
    "instagram_publish_executed": False,
    "real_action_executed": False,
}

BLOCKED_TERMS = [
    "access_token",
    "password",
    "secret",
    "api_key",
    "paradaatlantida",
    "parada atlantida",
    "17841480166187766",
    "869334472930140",
    "--execute-real-publish",
    "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW",
    "KOS_REAL_HUPMIX_PUBLISH_ENABLED",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    return value.strip("-")[:100] or "orchestrator-request"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def find_blocked_terms(text: str) -> list[str]:
    low = text.lower()
    return [term for term in BLOCKED_TERMS if term.lower() in low]


def classify_request(text: str) -> str:
    low = text.lower()

    if any(word in low for word in ["instagram", "hupmix", "post", "postar", "publicar", "rede", "social", "campanha", "conteudo", "conteúdo"]):
        return "social_publish"

    if any(word in low for word in ["saas", "produto", "app", "landing", "mvp", "api", "cliente", "assinatura"]):
        return "products_saas"

    if any(word in low for word in ["agente", "orquestrador", "missao", "missão", "fila", "autonomia", "handoff", "scheduler"]):
        return "agents_orchestration"

    if any(word in low for word in ["patch", "codigo", "código", "corrigir", "bug", "refatorar", "arquivo"]):
        return "patches"

    if any(word in low for word in ["runtime", "status", "ligar", "desligar", "ponte", "chatgpt", "log"]):
        return "runtime_bridge"

    if any(word in low for word in ["admin", "administracao", "administração", "agenda", "rotina", "organizar", "pendencia", "pendência"]):
        return "admin"

    return "general"


def route_plan(route: str, request: str) -> dict[str, Any]:
    base = {
        "route": route,
        "summary": "",
        "recommended_modules": [],
        "safe_commands": [],
        "requires_human_gate": True,
        "can_auto_execute_now": False,
    }

    if route == "social_publish":
        low = request.lower()
        target = "casa_da_limpeza" if "casa da limpeza" in low or "ki-publica" in low or "ki publica" in low else "hupmix"
        label = "Ki-Publica/Casa da Limpeza" if target == "casa_da_limpeza" else "Hupmix"
        base["summary"] = "Pedido relacionado a redes sociais, estrategia, readiness ou publicacao " + label + "."
        base["recommended_modules"] = ["Ki-Publica capability pack", "71B Social Strategy Generator", "71C Publish Readiness", "69F/69G/69H gates existentes"]
        base["safe_commands"] = [
            "python scripts\\run_phase71b_social_strategy_generator.py --target " + target + " --objective \"descrever objetivo\" --campaign " + target.replace("_", "-") + "-weekly",
            "python scripts\\run_phase71c_social_publish_readiness_auditor.py --target " + target + " --asset-url https://example.com/imagem.png --caption \"legenda sem publicar\"",
            "C:\\Users\\oi\\Desktop\\KOS_Social_Ops_Control_Center.cmd",
        ]
        return base

    if route == "products_saas":
        base["summary"] = "Pedido relacionado a produto, SaaS, MVP, landing, app ou oferta."
        base["recommended_modules"] = ["Product Factory", "Product Registry", "Scaffold Preview", "QA Gate", "Export Packager"]
        base["safe_commands"] = [
            "C:\\Users\\oi\\Desktop\\KOS_Unified_Command_Cockpit.cmd",
            "git --no-pager status --short",
        ]
        return base

    if route == "agents_orchestration":
        base["summary"] = "Pedido relacionado a agentes, missoes, filas, autonomia ou handoff."
        base["recommended_modules"] = ["Autonomy Operations Dashboard", "Mission Queue", "Engineer Handoff", "Runtime Control"]
        base["safe_commands"] = [
            "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status",
            "C:\\Users\\oi\\Desktop\\KOS_Unified_Command_Cockpit.cmd",
        ]
        return base

    if route == "patches":
        base["summary"] = "Pedido relacionado a alteracao de codigo, correcao ou proposta de patch."
        base["recommended_modules"] = ["70A Safe Patch Proposer", "70B Safe Patch Review Panel"]
        base["safe_commands"] = [
            "python scripts\\run_phase70a_safe_patch_proposer.py --objective \"descrever melhoria\" --files README.md",
            "C:\\Users\\oi\\Desktop\\KOS_Safe_Patch_Review_Panel.cmd",
        ]
        return base

    if route == "runtime_bridge":
        base["summary"] = "Pedido relacionado a runtime, logs, ponte ChatGPT ou status operacional."
        base["recommended_modules"] = ["70C ChatGPT Bridge", "70D Drop Watcher", "70E Runtime Controller", "49 Runtime Control"]
        base["safe_commands"] = [
            "powershell -ExecutionPolicy Bypass -File scripts\\kos_chatgpt_bridge_runtime_control.ps1 -Action status",
            "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status",
        ]
        return base

    if route == "admin":
        base["summary"] = "Pedido relacionado a administracao, rotina, agenda ou organizacao."
        base["recommended_modules"] = ["72A Weekly Operator Workspace", "72B Unified Command Cockpit"]
        base["safe_commands"] = [
            "C:\\Users\\oi\\Desktop\\KOS_Weekly_Operator_Workspace.cmd",
            "C:\\Users\\oi\\Desktop\\KOS_Unified_Command_Cockpit.cmd",
        ]
        return base

    base["summary"] = "Pedido geral. Orquestrador deve revisar contexto e escolher modulo seguro."
    base["recommended_modules"] = ["72B Unified Command Cockpit", "72A Weekly Workspace"]
    base["safe_commands"] = [
        "C:\\Users\\oi\\Desktop\\KOS_Unified_Command_Cockpit.cmd",
        "git --no-pager status --short",
    ]
    return base


def build_context_snapshot() -> dict[str, Any]:
    inventory = read_json(LATEST_INVENTORY)

    reports = {
        "72B_cockpit": read_json(ROOT / "reports/KOS_PHASE72B_UNIFIED_COMMAND_COCKPIT_BOOTSTRAP.json").get("status"),
        "72A_weekly": read_json(ROOT / "reports/KOS_PHASE72A_WEEKLY_OPERATOR_WORKSPACE_BOOTSTRAP.json").get("status"),
        "71A_social": read_json(ROOT / "reports/KOS_PHASE71A_SOCIAL_OPS_CONTROL_CENTER_BOOTSTRAP.json").get("status"),
        "71B_strategy": read_json(ROOT / "reports/KOS_PHASE71B_SOCIAL_STRATEGY_GENERATOR_BOOTSTRAP.json").get("status"),
        "71C_readiness": read_json(ROOT / "reports/KOS_PHASE71C_SOCIAL_PUBLISH_READINESS_AUDITOR_BOOTSTRAP.json").get("status"),
        "70_1_bridge": read_json(ROOT / "reports/KOS_PHASE701_CHATGPT_LOCAL_BRIDGE_BASELINE_CERTIFICATION.json").get("status"),
        "69H_publish_executor": read_json(ROOT / "reports/KOS_PHASE69H_HUPMIX_REAL_PUBLISH_EXECUTOR_BOOTSTRAP.json").get("status"),
    }

    return {
        "inventory_status": inventory.get("status"),
        "inventory_counts": inventory.get("counts", {}),
        "key_reports": reports,
        "safe_flags": SAFE_FLAGS,
    }


def process_request(request: str, request_id: str = "") -> dict[str, Any]:
    request = request.strip()
    request_id = slug(request_id or f"request-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

    blocked = find_blocked_terms(request)
    route = classify_request(request)
    plan = route_plan(route, request)
    context = build_context_snapshot()

    status = "KOS_ORCHESTRATOR_REQUEST_REVIEW_READY"
    if blocked:
        status = "KOS_ORCHESTRATOR_REQUEST_BLOCKED_FOR_REVIEW"
        plan["can_auto_execute_now"] = False
        plan["requires_human_gate"] = True

    payload = {
        "status": status,
        "phase": "72C",
        "request_id": request_id,
        "request": request,
        "route": route,
        "blocked_terms": blocked,
        "plan": plan,
        "context_snapshot": context,
        "decision": {
            "execute_now": False,
            "reason": "Caixa do orquestrador gera rota, plano e comandos seguros. Execucao perigosa exige gate humano.",
            "next_step": "operador revisa plano no cockpit e executa apenas comandos seguros",
        },
        **SAFE_FLAGS,
        "created_at": now_iso(),
    }

    payload["request_sha256"] = sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    INBOX.mkdir(parents=True, exist_ok=True)
    RESPONSES.mkdir(parents=True, exist_ok=True)

    write_json(INBOX / f"{request_id}.json", {
        "request_id": request_id,
        "request": request,
        "created_at": payload["created_at"],
        "request_sha256": payload["request_sha256"],
    })

    write_json(RESPONSES / f"{request_id}.json", payload)
    write_json(LATEST_RESPONSE, payload)

    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--request-id", default="")
    args = parser.parse_args()

    result = process_request(request=args.request, request_id=args.request_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
