from __future__ import annotations

import argparse
import json
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "local_runtime" / "kos_action_router"
MEMORY_DIR = ROOT / "memory" / "kos_action_router"
LATEST_PACKET = RUNTIME_DIR / "latest_action_packet.json"
EVENTS = RUNTIME_DIR / "events.jsonl"
TOOL_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_TOOL_REGISTRY.json"
CONNECTION_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_CONNECTION_REGISTRY.json"
PACK_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_PRODUCT_CAPABILITY_PACKS.json"
TENANT_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_TENANT_REGISTRY.json"
ORCHESTRATOR_CONSCIOUSNESS = ROOT / "memory" / "kos_governance" / "KOS_ORCHESTRATOR_CONSCIOUSNESS_V1.md"

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
        "label": "Ki-Publica / redes sociais / campanhas",
        "modules": [
            "Ki-Publica capability pack",
            "71B Social Strategy Generator",
            "71C Social Publish Readiness Auditor",
            "Safe Action / Human Gate"
        ],
        "next_step": "Preparar plano de campanha em rascunho e revisar antes de qualquer acao real.",
        "risk": "Publicacao automatica bloqueada. Instagram real exige confirmacao humana explicita.",
        "safe_action": "Gerar plano operacional de campanha sem publicar.",
        "internal_commands": [
            "python scripts\\run_phase71b_social_strategy_generator.py --target <tenant_id> --objective \"<objetivo>\" --campaign <campaign_id>",
            "python scripts\\run_phase71c_social_publish_readiness_auditor.py --target <tenant_id> --asset-url \"<asset>\" --caption \"<legenda>\""
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
    "connections_status": {
        "label": "Conexoes / credenciais / deploy targets",
        "modules": [
            "Connection Registry",
            "Secrets Manager status mascarado",
            "Capabilities read-only",
            "Render/Vercel/Git config check"
        ],
        "next_step": "Validar conexoes em modo somente leitura, sem expor tokens e sem acao externa real.",
        "risk": "Valores secretos ficam ocultos. Nenhum deploy, envio, publish ou chamada paga sera executado.",
        "safe_action": "Gerar diagnostico read-only de conexoes.",
        "internal_commands": [
            "$env:PYTHONIOENCODING='utf-8'; python -m k_atlas.core.capabilities",
            "$env:PYTHONIOENCODING='utf-8'; python -m k_atlas.core.secrets_manager"
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


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def registry_snapshot() -> dict:
    tools = read_json(TOOL_REGISTRY)
    connections = read_json(CONNECTION_REGISTRY)
    packs = read_json(PACK_REGISTRY)
    tenants = read_json(TENANT_REGISTRY)
    return {
        "tool_registry_status": tools.get("status"),
        "connection_registry_status": connections.get("status"),
        "product_pack_registry_status": packs.get("status"),
        "tenant_registry_status": tenants.get("status"),
        "tool_count": len(tools.get("tools", []) or []),
        "connection_count": len(connections.get("connections", []) or []),
        "product_pack_count": len(packs.get("packs", []) or []),
        "tenant_count": len(tenants.get("tenants", []) or []),
        "registry_files": {
            "tools": str(TOOL_REGISTRY),
            "connections": str(CONNECTION_REGISTRY),
            "product_capability_packs": str(PACK_REGISTRY),
            "tenants": str(TENANT_REGISTRY),
            "orchestrator_consciousness": str(ORCHESTRATOR_CONSCIOUSNESS),
        },
    }


def consciousness_snapshot() -> dict:
    if not ORCHESTRATOR_CONSCIOUSNESS.exists():
        return {
            "status": "KOS_ORCHESTRATOR_CONSCIOUSNESS_MISSING",
            "path": str(ORCHESTRATOR_CONSCIOUSNESS),
            "active": False,
        }

    text = ORCHESTRATOR_CONSCIOUSNESS.read_text(encoding="utf-8-sig", errors="replace")
    return {
        "status": "KOS_ORCHESTRATOR_CONSCIOUSNESS_ACTIVE",
        "version": "V1",
        "path": str(ORCHESTRATOR_CONSCIOUSNESS),
        "active": True,
        "role": "memoria raiz da IA base do K-OS",
        "mission": "transformar inteligencia artificial em operacao real, segura, modular, auditavel e reutilizavel",
        "operating_cycle": [
            "entender pedido",
            "identificar projeto/contexto",
            "consultar memoria existente",
            "verificar capacidades instaladas",
            "verificar integracoes ativas e inativas",
            "avaliar risco",
            "escolher rota",
            "executar apenas acoes seguras",
            "bloquear acao externa sem Human Gate",
            "registrar evento",
            "transformar aprendizado em modulo reutilizavel",
            "sugerir proximo passo exato",
        ],
        "known_projects": [
            "K-OS / K-Atlas",
            "Hupmix",
            "Garoto Oxy Power",
            "Manus / Pacote Hupmix",
            "Portal Atlantida",
            "Parada Atlantida",
        ],
        "core_values": [
            "estabilidade antes de expansao",
            "simplicidade antes de complexidade",
            "execucao antes de teoria",
            "memoria antes de improviso",
            "Human Gate antes de acao externa",
            "produto antes de acumulo de scripts",
        ],
        "source_chars": len(text),
    }


def tools_by_id() -> dict:
    data = read_json(TOOL_REGISTRY)
    return {str(item.get("id")): item for item in data.get("tools", []) or [] if item.get("id")}


def find_tool(tool_id: str) -> dict:
    return tools_by_id().get(tool_id, {})


def commands_for(tool_ids: list[str]) -> list[str]:
    commands = []
    for tool_id in tool_ids:
        command = find_tool(tool_id).get("command")
        if command:
            commands.append(str(command))
    return commands


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def normalize_ascii(text: str) -> str:
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
    return str(text or "").lower().translate(table)


def resolve_tenant(request: str) -> dict:
    text = normalize_ascii(request)
    registry = read_json(TENANT_REGISTRY)
    for tenant in registry.get("tenants", []) or []:
        aliases = [tenant.get("id", ""), tenant.get("name", "")]
        aliases.extend(tenant.get("aliases", []) or [])
        if any(normalize_ascii(alias) in text for alias in aliases if alias):
            return tenant
    return {}


def resolve_product_pack(request: str, tenant: dict) -> dict:
    text = normalize_ascii(request)
    registry = read_json(PACK_REGISTRY)
    packs = registry.get("packs", []) or []
    tenant_packs = tenant.get("capability_packs", []) or []

    for pack in packs:
        aliases = [pack.get("id", ""), pack.get("name", "")]
        if any(normalize_ascii(alias) in text for alias in aliases if alias):
            return pack

    if tenant_packs:
        for pack in packs:
            if pack.get("id") == tenant_packs[0]:
                return pack

    return {}


def route_tool_ids(route: str) -> list[str]:
    if route == "social_publish":
        return ["ki_publica_campaign_draft", "social_publish_readiness", "safe_action_executor"]
    if route == "products_saas":
        return ["product_factory_draft", "saas_product_mission_pack", "safe_action_executor"]
    if route == "agents_orchestration":
        return ["mission_queue_status", "runtime_control_status"]
    if route == "runtime_bridge":
        return ["chatgpt_bridge_status", "runtime_control_status"]
    if route == "connections_status":
        return ["connection_status"]
    if route == "instagram_accounts_status":
        return ["connection_status", "safe_action_executor"]
    if route == "email_ops":
        return ["connection_status", "safe_action_executor"]
    if route == "local_files_downloads":
        return ["safe_action_executor"]
    if route == "admin":
        return ["weekly_operator_workspace"]
    if route == "patches":
        return ["safe_action_executor"]
    return ["safe_action_executor"]


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



ROUTES["social_read"] = {
    "label": "Redes sociais / Hupmix / leitura segura",
    "modules": [
        "Social Ops Read-Only",
        "Social Publish Readiness Auditor",
        "Human Decision Gate",
    ],
    "next_step": "Receber link, print, legenda ou texto da publicacao para analise segura.",
    "risk": "Nao acessar Instagram logado, nao automatizar navegador, nao mexer em cookies e nao fazer scraping.",
    "safe_action": "Analisar publicacao fornecida pelo operador.",
    "internal_commands": [],
    "commands": [],
}

ROUTES["instagram_accounts_status"] = {
    "label": "Instagram / contas conectadas / Meta Graph",
    "modules": [
        "Meta Graph read-only",
        "Instagram account audit",
        "Connection Registry",
        "Safe Action / Human Gate",
    ],
    "next_step": "Listar contas Instagram registradas e validar, em modo read-only, quais respondem pelo conector oficial.",
    "risk": "Sem navegador logado, sem scraping, sem publicar e sem imprimir token.",
    "safe_action": "Auditar contas Instagram conectadas e mostrar evidencia sanitizada.",
    "internal_commands": [
        "python scripts\\run_phase69d_hupmix_instagram_audit.py"
    ],
    "commands": [],
}

ROUTES["email_ops"] = {
    "label": "Email / Gmail / inbox",
    "modules": [
        "Gmail OAuth readiness",
        "Connection Registry",
        "Inbox review planner",
        "Safe Action / Human Gate",
    ],
    "next_step": "Verificar se Gmail/OAuth esta conectado e, se estiver pronto, preparar leitura segura da inbox.",
    "risk": "Sem envio, exclusao, arquivamento ou leitura de segredo. Email real exige conector OAuth configurado.",
    "safe_action": "Auditar readiness de email e preparar proxima acao segura.",
    "internal_commands": [
        "$env:PYTHONIOENCODING='utf-8'; python -m k_atlas.core.capabilities",
        "python scripts\\run_gmail_read_only_audit.py --limit 10"
    ],
    "commands": [],
}

ROUTES["local_files_downloads"] = {
    "label": "Computador local / Downloads / organizacao",
    "modules": [
        "Local file inventory",
        "Downloads organizer plan",
        "Human Gate",
    ],
    "next_step": "Ler a pasta Downloads em modo inventario e propor organizacao sem mover arquivos automaticamente.",
    "risk": "Nenhum arquivo sera movido, apagado ou renomeado sem confirmacao humana explicita.",
    "safe_action": "Gerar inventario e plano de organizacao da pasta Downloads.",
    "internal_commands": [],
    "commands": [],
}


def normalize_social_intent_text(value: str) -> str:
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
    return str(value or "").lower().translate(table)


def is_social_read_request(request: str) -> bool:
    text = normalize_social_intent_text(request)

    social_markers = [
        "hupmix", "instagram", "post", "publicacao", "publicacoes",
        "reels", "story", "stories", "perfil"
    ]

    read_markers = [
        "veja", "ver", "olhar", "olhe", "ultima", "ultimo",
        "analisar", "analise", "avaliar", "auditar", "revisar",
        "ler", "leia"
    ]

    strong_create_markers = [
        "criar campanha", "gerar campanha", "campanha para",
        "campanha de 7", "7 dias", "calendario", "conteudo para semana"
    ]

    has_social = any(word in text for word in social_markers)
    has_read = any(word in text for word in read_markers)
    has_strong_create = any(word in text for word in strong_create_markers)

    if not has_social or not has_read:
        return False

    if has_strong_create and "ultima" not in text and "ultimo" not in text and "ver" not in text and "veja" not in text:
        return False

    return True


def detect_route(request: str, base: dict) -> str:
    text = normalize(request)
    ascii_text = normalize_ascii(request)
    instagram_status_words = ["instagram conectado", "instagram conectados", "instagrams conectados", "contas instagram", "quais instagram", "qual instagram", "perfis instagram", "instagram estao conectados", "instagram esta conectado"]
    if "instagram" in ascii_text and any(w in ascii_text for w in instagram_status_words + ["conectado", "conectados", "conta", "contas", "perfil", "perfis"]):
        return "instagram_accounts_status"

    email_words = ["email", "emails", "e-mail", "e-mails", "gmail", "inbox", "caixa de entrada", "correio"]
    email_action_words = ["revise", "revisar", "ver", "ler", "leia", "organize", "organizar", "triagem", "resuma", "resumir"]
    if any(w in ascii_text for w in email_words) and any(w in ascii_text for w in email_action_words + ["conectado", "conexao", "status"]):
        return "email_ops"

    downloads_words = ["downloads", "download", "pasta downloads", "meus downloads"]
    file_org_words = ["organize", "organizar", "arrumar", "limpar", "classificar", "separar", "computador", "arquivos"]
    if any(w in ascii_text for w in downloads_words) and any(w in ascii_text for w in file_org_words):
        return "local_files_downloads"

    if is_social_read_request(request):
        return "social_read"
    connection_words = ["conexao", "conexoes", "conectado", "conectados", "credencial", "credenciais", "token", "secret", "secrets", "gemini", "supabase", "meta", "google", "gmail", "github", "render", "vercel", "oauth"]
    if any(w in ascii_text for w in connection_words):
        return "connections_status"
    base_route = base.get("route")
    if base_route in ROUTES:
        return base_route

    social_words = ["ki-publica", "ki publica", "casa da limpeza", "hupmix", "instagram", "campanha", "post", "reels", "story", "stories", "publicar", "social"]
    product_words = ["saas", "produto", "mvp", "landing", "app", "startup", "projeto"]
    agent_words = ["agente", "agentes", "status", "fila", "missao", "missao", "orquestrador", "atenção", "atencao"]
    patch_words = ["corrigir", "bug", "patch", "codigo", "código", "arquivo", "implementar"]
    runtime_words = ["bridge", "chatgpt", "runtime", "watcher", "log", "porta", "streamlit"]
    admin_words = ["rotina", "prioridade", "organizar", "agenda", "semana", "admin"]

    if any(w in ascii_text for w in social_words):
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

    if route == "social_read":
        return request
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
    tenant = resolve_tenant(request)
    product_pack = resolve_product_pack(request, tenant)
    spec = ROUTES.get(route, ROUTES["general"])
    tool_ids = route_tool_ids(route)
    registry_commands = commands_for(tool_ids) or spec["internal_commands"]
    consciousness = consciousness_snapshot()
    packet_id = "kos_action_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]

    route_label = spec["label"]
    if tenant:
        route_label = route_label + " / " + str(tenant.get("name", tenant.get("id")))
    if product_pack and product_pack.get("id") == "ki_publica" and "Ki-Publica" not in route_label:
        route_label = "Ki-Publica / " + route_label

    modules = list(spec["modules"])
    if product_pack:
        modules.insert(0, str(product_pack.get("name", product_pack.get("id"))) + " capability pack")
    if tenant:
        modules.insert(0, "Tenant: " + str(tenant.get("name", tenant.get("id"))))

    packet = {
        "status": "KOS_ACTION_PACKET_READY",
        "packet_id": packet_id,
        "created_at": now_iso(),
        "request": request,
        "route": route,
        "route_label": route_label,
        "tenant": tenant or None,
        "product_capability_pack": product_pack or None,
        "tool_ids": tool_ids,
        "operator_response": {
            "entendi": summarize_request(request, route),
            "vou_usar_estes_modulos": modules,
            "proximo_passo": spec["next_step"],
            "risco_bloqueio": spec["risk"],
            "acao_segura_disponivel": spec["safe_action"],
            "confirmacao_por_texto": "Responda com confirmar, alterar <ajuste>, cancelar ou continuar. Acoes reais continuam bloqueadas por Human Gate.",
        },
        "action_packet": {
            "route": route,
            "intent_summary": summarize_request(request, route),
            "orchestrator_consciousness_status": consciousness.get("status"),
            "orchestrator_mission": consciousness.get("mission"),
            "modules": modules,
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
            "internal_commands_hidden_by_default": registry_commands,
            "registry_tool_ids": tool_ids,
        },
        "locks": LOCKS,
        "evidence": {
            "registry_snapshot": registry_snapshot(),
            "orchestrator_consciousness": consciousness,
            "router_runtime_dir": str(RUNTIME_DIR),
            "latest_packet": str(LATEST_PACKET),
            "external_action_executed": False,
            "secret_values_exposed": False,
        },
        "source_72c": {
            "status": base.get("status"),
            "route": base.get("route"),
            "returncode": base.get("returncode"),
        },
    }
    return packet


def save_packet(packet: dict) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    packet_path = RUNTIME_DIR / f"{packet['packet_id']}.json"
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
