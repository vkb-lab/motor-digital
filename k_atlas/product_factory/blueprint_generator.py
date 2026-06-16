from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import uuid

ROOT = Path(__file__).resolve().parents[2]
MISSION_LOG = ROOT / "local_runtime" / "product_factory" / "product_missions.jsonl"
BLUEPRINT_DIR = ROOT / "local_runtime" / "product_factory_blueprints"
BLUEPRINT_INDEX = BLUEPRINT_DIR / "blueprints_index.jsonl"
SUMMARY_PATH = BLUEPRINT_DIR / "latest_blueprint_summary.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "product-blueprint"

def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            pass
    return items

def get_latest_product_mission() -> dict:
    items = _read_jsonl(MISSION_LOG)
    return items[-1] if items else {}

def module_plan(product_type: str) -> list[dict]:
    modules = [
        {"key": "core", "name": "Core", "purpose": "Regras centrais e estado operacional."},
        {"key": "ui", "name": "Interface", "purpose": "Cockpit ou tela inicial."},
        {"key": "storage", "name": "Persistencia", "purpose": "JSON-first, banco depois."},
        {"key": "audit", "name": "Auditoria", "purpose": "Logs, eventos e evidencias."},
        {"key": "governance", "name": "Governanca", "purpose": "Gates, permissoes e rollback."}
    ]

    extras = {
        "saas": "Planos, workspace e operacao por cliente.",
        "app": "Telas, fluxo principal e estado do app.",
        "landing_page": "Copy, secoes, CTA e captura local.",
        "campaign": "Calendario, canais, criativos e aprovacao.",
        "automation": "Gatilhos, acoes, logs e dry-run.",
        "api": "Rotas, payloads, erros e auth futura.",
        "agent": "Papel, memoria, permissoes e limites.",
        "dashboard": "Metricas, cards, tabelas e visualizacoes.",
        "integration": "Conector, sandbox, limites e logs."
    }

    modules.append({
        "key": product_type,
        "name": "Modulo especifico",
        "purpose": extras.get(product_type, extras["saas"])
    })

    return modules

def route_plan(product_type: str, slug: str) -> list[dict]:
    if product_type == "api":
        return [
            {"path": "/health", "method": "GET", "purpose": "Status."},
            {"path": f"/api/{slug}", "method": "GET", "purpose": "Listagem futura."},
            {"path": f"/api/{slug}", "method": "POST", "purpose": "Criacao futura com gate."}
        ]
    if product_type == "landing_page":
        return [
            {"path": "/", "name": "Landing", "purpose": "Promessa, prova e CTA."},
            {"path": "/obrigado", "name": "Obrigado", "purpose": "Confirmacao local."}
        ]
    return [
        {"path": "/", "name": "Home", "purpose": "Entrada principal."},
        {"path": "/workspace", "name": "Workspace", "purpose": "Operacao."},
        {"path": "/settings", "name": "Settings", "purpose": "Configuracoes."}
    ]

def data_model(product_type: str) -> list[dict]:
    return [
        {"entity": "User", "fields": ["id", "name", "role", "created_at"], "storage": "future_database"},
        {"entity": "EventLog", "fields": ["id", "event_type", "payload", "created_at"], "storage": "jsonl_first"},
        {"entity": "ProductRecord", "fields": ["id", "type", "status", "payload"], "storage": "json_first", "product_type": product_type}
    ]

def build_blueprint_from_mission(mission: dict) -> dict:
    title = mission.get("title") or "Nova missao de produto"
    slug = mission.get("slug") or slugify(title)
    product_type = mission.get("product_type") or "saas"

    return {
        "status": "PRODUCT_BLUEPRINT_READY",
        "blueprint_id": "PFB-" + uuid.uuid4().hex[:12].upper(),
        "source_mission_id": mission.get("mission_id"),
        "title": title,
        "slug": slug,
        "product_type": product_type,
        "execution_mode": "DESIGN_ONLY",
        "product_brief": {
            "target_user": mission.get("target_user"),
            "market": mission.get("market"),
            "promise": f"Resolver um problema claro para {mission.get('target_user', 'usuario alvo')}.",
            "mvp_goal": "Validar valor com a menor versao operacional possivel.",
            "success_criteria": [
                "Escopo MVP claro",
                "Operacao auditavel",
                "Sem dependencia externa obrigatoria",
                "Aprovacao humana antes de execucao"
            ]
        },
        "mvp_scope": {
            "included": [
                "Interface inicial",
                "Persistencia JSON-first",
                "Logs operacionais",
                "Gates de seguranca",
                "Plano de evolucao modular"
            ],
            "excluded_now": [
                "Deploy automatico",
                "IA paga",
                "Publicacao externa",
                "Credenciais reais",
                "Codex automatico"
            ]
        },
        "architecture": {
            "stack": ["Python", "Streamlit", "JSON", "GitHub", "local runtime"],
            "modules": module_plan(product_type),
            "routes_or_screens": route_plan(product_type, slug),
            "data_model": data_model(product_type)
        },
        "automation_plan": [
            {"step": "capture", "description": "Registrar entrada do operador."},
            {"step": "plan", "description": "Gerar plano tecnico em dry-run."},
            {"step": "approve", "description": "Exigir aprovacao humana."},
            {"step": "execute_future", "description": "Executar apenas em fase futura."},
            {"step": "audit", "description": "Registrar evidencias."}
        ],
        "launch_plan": {
            "phase_1": "Prototipo local.",
            "phase_2": "Validacao interna.",
            "phase_3": "Aprovacao humana.",
            "phase_4": "Deploy reversivel futuro."
        },
        "risk_register": [
            {"risk": "escopo grande demais", "mitigation": "reduzir MVP", "severity": "medium"},
            {"risk": "dependencia externa precoce", "mitigation": "usar mocks locais", "severity": "medium"},
            {"risk": "execucao sem aprovacao", "mitigation": "manter gates bloqueados", "severity": "high"}
        ],
        "acceptance_criteria": [
            "Blueprint criado sem execucao real",
            "Gates bloqueados",
            "Arquitetura modular definida",
            "MVP definido",
            "Riscos registrados"
        ],
        "gates": {
            "execution_allowed": False,
            "build_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "codex_auto_execute_allowed": False,
            "external_publish_allowed": False,
            "human_approval_required": True
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def save_blueprint(blueprint: dict) -> dict:
    BLUEPRINT_DIR.mkdir(parents=True, exist_ok=True)

    slug = blueprint.get("slug") or "product-blueprint"
    blueprint_id = blueprint.get("blueprint_id") or "PFB-UNKNOWN"
    path = BLUEPRINT_DIR / f"{slug}_{blueprint_id}.json"

    path.write_text(json.dumps(blueprint, ensure_ascii=False, indent=2), encoding="utf-8")

    index_item = {
        "blueprint_id": blueprint_id,
        "source_mission_id": blueprint.get("source_mission_id"),
        "title": blueprint.get("title"),
        "product_type": blueprint.get("product_type"),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "created_at": blueprint.get("created_at"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }

    with BLUEPRINT_INDEX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(index_item, ensure_ascii=False) + "\n")

    summary = summarize_blueprints(limit=20)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "PRODUCT_BLUEPRINT_SAVED",
        "blueprint_id": blueprint_id,
        "path": index_item["path"],
        "index_item": index_item,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }

def generate_blueprint_from_latest_mission() -> dict:
    mission = get_latest_product_mission()
    if not mission:
        return {
            "status": "NO_PRODUCT_MISSION_FOUND",
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    blueprint = build_blueprint_from_mission(mission)
    save_result = save_blueprint(blueprint)

    return {
        "status": "PRODUCT_BLUEPRINT_GENERATED_FROM_LATEST_MISSION",
        "blueprint": blueprint,
        "save_result": save_result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False
    }

def summarize_blueprints(limit: int = 20) -> dict:
    entries = _read_jsonl(BLUEPRINT_INDEX)[-limit:]
    latest = entries[-1] if entries else {}

    by_type = {}
    for item in entries:
        ptype = item.get("product_type", "unknown")
        by_type[ptype] = by_type.get(ptype, 0) + 1

    return {
        "status": "PRODUCT_BLUEPRINT_SUMMARY_READY",
        "index_exists": BLUEPRINT_INDEX.exists(),
        "index_path": str(BLUEPRINT_INDEX.relative_to(ROOT)).replace("\\", "/"),
        "entries_returned": len(entries),
        "latest_blueprint_id": latest.get("blueprint_id"),
        "latest_title": latest.get("title"),
        "latest_product_type": latest.get("product_type"),
        "by_type": by_type,
        "last_entries": entries,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }
