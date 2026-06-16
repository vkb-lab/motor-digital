from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import uuid

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_INDEX = ROOT / "local_runtime" / "product_factory_blueprints" / "blueprints_index.jsonl"
BUILD_PLAN_DIR = ROOT / "local_runtime" / "product_factory_build_plans"
BUILD_PLAN_INDEX = BUILD_PLAN_DIR / "build_plans_index.jsonl"
SUMMARY_PATH = BUILD_PLAN_DIR / "latest_build_plan_summary.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "product-build-plan"

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

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

def get_latest_blueprint() -> dict:
    index = _read_jsonl(BLUEPRINT_INDEX)
    if not index:
        return {}

    latest = index[-1]
    path = latest.get("path")
    if not path:
        return {}

    return _read_json(ROOT / path)

def suggested_files(product_type: str, slug: str) -> list[dict]:
    base = [
        {"path": f"products/{slug}/README.md", "purpose": "Documentacao operacional do produto."},
        {"path": f"products/{slug}/config/product_policy.json", "purpose": "Politica e gates do produto."},
        {"path": f"products/{slug}/core/state.py", "purpose": "Estado operacional e persistencia."},
        {"path": f"products/{slug}/core/events.py", "purpose": "Registro de eventos e auditoria."},
        {"path": f"products/{slug}/app.py", "purpose": "Interface inicial Streamlit."},
        {"path": f"products/{slug}/tests/test_product_safety.py", "purpose": "Testes de gates e seguranca."}
    ]

    extras = {
        "saas": [
            {"path": f"products/{slug}/core/workspace.py", "purpose": "Workspace inicial do SaaS."},
            {"path": f"products/{slug}/core/customer.py", "purpose": "Modelo futuro de cliente."}
        ],
        "landing_page": [
            {"path": f"products/{slug}/content/copy.md", "purpose": "Copy da landing page."},
            {"path": f"products/{slug}/content/sections.json", "purpose": "Estrutura das secoes."}
        ],
        "campaign": [
            {"path": f"products/{slug}/campaign/calendar.json", "purpose": "Calendario de campanha."},
            {"path": f"products/{slug}/campaign/assets.json", "purpose": "Pecas e variacoes para aprovacao."}
        ],
        "automation": [
            {"path": f"products/{slug}/automation/flow.json", "purpose": "Fluxo de automacao em dry-run."},
            {"path": f"products/{slug}/automation/runner.py", "purpose": "Runner futuro bloqueado por gates."}
        ],
        "api": [
            {"path": f"products/{slug}/api/routes.py", "purpose": "Rotas futuras da API."},
            {"path": f"products/{slug}/api/schemas.py", "purpose": "Schemas de entrada e saida."}
        ],
        "agent": [
            {"path": f"products/{slug}/agent/profile.json", "purpose": "Papel, permissoes e limites."},
            {"path": f"products/{slug}/agent/memory_policy.json", "purpose": "Politica de memoria do agente."}
        ],
        "dashboard": [
            {"path": f"products/{slug}/dashboard/metrics.json", "purpose": "Metricas principais."},
            {"path": f"products/{slug}/dashboard/views.py", "purpose": "Views futuras."}
        ],
        "integration": [
            {"path": f"products/{slug}/integration/adapter.py", "purpose": "Adaptador desacoplado."},
            {"path": f"products/{slug}/integration/sandbox.py", "purpose": "Sandbox local."}
        ],
        "app": [
            {"path": f"products/{slug}/app/screens.py", "purpose": "Telas futuras."},
            {"path": f"products/{slug}/app/session.py", "purpose": "Estado de sessao."}
        ]
    }

    return base + extras.get(product_type, extras["saas"])

def build_plan_from_blueprint(blueprint: dict) -> dict:
    title = blueprint.get("title") or "Produto sem titulo"
    slug = blueprint.get("slug") or slugify(title)
    product_type = blueprint.get("product_type") or "saas"

    plan = {
        "status": "PRODUCT_BUILD_PLAN_READY",
        "build_plan_id": "PFBP-" + uuid.uuid4().hex[:12].upper(),
        "source_blueprint_id": blueprint.get("blueprint_id"),
        "source_mission_id": blueprint.get("source_mission_id"),
        "title": title,
        "slug": slug,
        "product_type": product_type,
        "execution_mode": "DRY_RUN_ONLY",
        "target_root": f"products/{slug}",
        "suggested_files": suggested_files(product_type, slug),
        "milestones": [
            {"id": "M1", "title": "Criar esqueleto local", "execution_allowed": False},
            {"id": "M2", "title": "Implementar core sem integracoes externas", "execution_allowed": False},
            {"id": "M3", "title": "Criar interface inicial", "execution_allowed": False},
            {"id": "M4", "title": "Criar testes de seguranca", "execution_allowed": False},
            {"id": "M5", "title": "Revisao humana antes de build real", "execution_allowed": False}
        ],
        "dry_run_commands": [
            {"label": "Ver status Git", "command": "git --no-pager status --short"},
            {"label": "Rodar testes existentes", "command": "python -m pytest -q"},
            {"label": "Health K-OS", "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action health"}
        ],
        "test_plan": [
            "Testar gates bloqueados",
            "Testar criacao de estado local",
            "Testar logs auditaveis",
            "Testar ausencia de chamada externa",
            "Testar ausencia de IA paga"
        ],
        "acceptance_criteria": [
            "Plano criado sem escrever produto real",
            "Nenhum deploy executado",
            "Nenhuma IA paga chamada",
            "Nenhuma publicacao externa feita",
            "Arquivos sugeridos revisaveis pelo operador"
        ],
        "gates": {
            "write_product_code_allowed": False,
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

    return plan

def save_build_plan(plan: dict) -> dict:
    BUILD_PLAN_DIR.mkdir(parents=True, exist_ok=True)

    slug = plan.get("slug") or "product-build-plan"
    plan_id = plan.get("build_plan_id") or "PFBP-UNKNOWN"
    path = BUILD_PLAN_DIR / f"{slug}_{plan_id}.json"

    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    index_item = {
        "build_plan_id": plan_id,
        "source_blueprint_id": plan.get("source_blueprint_id"),
        "title": plan.get("title"),
        "product_type": plan.get("product_type"),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "created_at": plan.get("created_at"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }

    with BUILD_PLAN_INDEX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(index_item, ensure_ascii=False) + "\n")

    summary = summarize_build_plans(limit=20)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "PRODUCT_BUILD_PLAN_SAVED",
        "build_plan_id": plan_id,
        "path": index_item["path"],
        "index_item": index_item,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }

def generate_build_plan_from_latest_blueprint() -> dict:
    blueprint = get_latest_blueprint()
    if not blueprint:
        return {
            "status": "NO_PRODUCT_BLUEPRINT_FOUND",
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    plan = build_plan_from_blueprint(blueprint)
    save_result = save_build_plan(plan)

    return {
        "status": "PRODUCT_BUILD_PLAN_GENERATED_FROM_LATEST_BLUEPRINT",
        "build_plan": plan,
        "save_result": save_result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False
    }

def summarize_build_plans(limit: int = 20) -> dict:
    entries = _read_jsonl(BUILD_PLAN_INDEX)[-limit:]
    latest = entries[-1] if entries else {}

    by_type = {}
    for item in entries:
        ptype = item.get("product_type", "unknown")
        by_type[ptype] = by_type.get(ptype, 0) + 1

    return {
        "status": "PRODUCT_BUILD_PLAN_SUMMARY_READY",
        "index_exists": BUILD_PLAN_INDEX.exists(),
        "index_path": str(BUILD_PLAN_INDEX.relative_to(ROOT)).replace("\\", "/"),
        "entries_returned": len(entries),
        "latest_build_plan_id": latest.get("build_plan_id"),
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
