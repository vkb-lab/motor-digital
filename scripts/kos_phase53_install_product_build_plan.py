from pathlib import Path
from datetime import datetime, timezone
import json
import re
import uuid

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

policy = {
    "status": "ACTIVE",
    "phase": "53",
    "module": "K-OS Product Factory Build Plan",
    "mode": "BUILD_PLAN_DRY_RUN_ONLY",
    "goal": "transformar blueprints em planos tecnicos de construcao sem executar build real",
    "blocked_actions": {
        "write_product_code_automatically": True,
        "build_product_automatically": True,
        "deploy_automatically": True,
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "auto_commit": True,
        "auto_push": True
    },
    "hard_rules": {
        "dry_run_only": True,
        "human_approval_required_before_build": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True
    },
    "created_at": now()
}

build_plan_code = r'''
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
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission
from k_atlas.product_factory.build_plan import generate_build_plan_from_latest_blueprint, summarize_build_plans

if __name__ == "__main__":
    create_product_mission(
        idea="Build plan demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase53_runner"
    )

    generate_blueprint_from_latest_mission()
    result = generate_build_plan_from_latest_blueprint()

    print(json.dumps({
        "status": "PHASE53_PRODUCT_BUILD_PLAN_GENERATED",
        "result_status": result.get("status"),
        "build_plan_id": result.get("build_plan", {}).get("build_plan_id"),
        "title": result.get("build_plan", {}).get("title"),
        "product_type": result.get("build_plan", {}).get("product_type"),
        "suggested_files_count": len(result.get("build_plan", {}).get("suggested_files", [])),
        "summary": summarize_build_plans(limit=10),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.product_factory.blueprint_generator import get_latest_product_mission, build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint, save_build_plan, summarize_build_plans

st.set_page_config(page_title="KOS Product Build Plan", layout="wide")

st.title("KOS Product Factory Build Plan")
st.caption("Transforma blueprint em plano tecnico de construcao. Dry-run only.")

mission = get_latest_product_mission()

if not mission:
    st.warning("Nenhuma missao local encontrada ainda.")
else:
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", plan.get("product_type"))
    col2.metric("Arquivos sugeridos", len(plan.get("suggested_files", [])))
    col3.metric("Build", "BLOQUEADO")
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Build Plan")
    st.json(plan)

    if st.button("Salvar build plan local", use_container_width=True):
        saved = save_build_plan(plan)
        st.success("Build plan salvo no runtime local.")
        st.json(saved)

st.subheader("Resumo")
st.json(summarize_build_plans(limit=20))

st.warning("Dry-run only. Nao cria produto real, nao executa build, nao usa IA paga, nao publica.")
'''

test_code = r'''
from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint, save_build_plan, summarize_build_plans

def test_build_plan_is_safe():
    mission = build_product_mission(
        idea="SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)

    assert plan["status"] == "PRODUCT_BUILD_PLAN_READY"
    assert plan["gates"]["write_product_code_allowed"] is False
    assert plan["gates"]["build_allowed"] is False
    assert plan["gates"]["deploy_allowed"] is False
    assert plan["gates"]["paid_ai_allowed"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False
    assert plan["external_side_effects_executed"] is False

def test_build_plan_has_required_sections():
    mission = build_product_mission(
        idea="API teste",
        product_type="api",
        target_user="dev",
        market="integracoes"
    )
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)

    assert "suggested_files" in plan
    assert "milestones" in plan
    assert "dry_run_commands" in plan
    assert "test_plan" in plan
    assert "acceptance_criteria" in plan
    assert len(plan["suggested_files"]) >= 1

def test_save_build_plan_and_summary_are_safe():
    mission = build_product_mission(
        idea="Dashboard teste",
        product_type="dashboard",
        target_user="operador",
        market="dados"
    )
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)
    saved = save_build_plan(plan)
    summary = summarize_build_plans(limit=5)

    assert saved["status"] == "PRODUCT_BUILD_PLAN_SAVED"
    assert summary["status"] == "PRODUCT_BUILD_PLAN_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_product_build_plan_policy.json", policy)
write(ROOT / "k_atlas" / "product_factory" / "build_plan.py", build_plan_code.strip() + "\n")

init_path = ROOT / "k_atlas" / "product_factory" / "__init__.py"
init_text = init_path.read_text(encoding="utf-8-sig") if init_path.exists() else ""
extra = "\nfrom .build_plan import build_plan_from_blueprint, generate_build_plan_from_latest_blueprint, summarize_build_plans\n"
if "build_plan" not in init_text:
    init_path.write_text(init_text.rstrip() + extra, encoding="utf-8")

write(ROOT / "scripts" / "run_phase53_product_build_plan_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Product_Build_Plan.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase53_product_build_plan.py", test_code.strip() + "\n")

report = {
    "status": "PHASE53_PRODUCT_BUILD_PLAN_BOOTSTRAPPED",
    "phase": "53",
    "created_files": [
        "config/kos_product_build_plan_policy.json",
        "k_atlas/product_factory/build_plan.py",
        "scripts/run_phase53_product_build_plan_demo.py",
        "pages/KOS_Product_Build_Plan.py",
        "tests/test_phase53_product_build_plan.py"
    ],
    "modified_files": [
        "k_atlas/product_factory/__init__.py"
    ],
    "runtime_files": [
        "local_runtime/product_factory_build_plans/build_plans_index.jsonl",
        "local_runtime/product_factory_build_plans/latest_build_plan_summary.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE53_PRODUCT_BUILD_PLAN_BOOTSTRAP.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))