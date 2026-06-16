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
    "phase": "52",
    "module": "K-OS Product Factory Blueprint Generator",
    "mode": "BLUEPRINT_DESIGN_ONLY",
    "goal": "transformar missoes de produto em blueprints completos sem build, deploy ou publicacao",
    "blocked_actions": {
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
        "design_only": True,
        "human_approval_required_before_execution": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True
    },
    "created_at": now()
}

blueprint_code = r'''
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
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission, summarize_blueprints

if __name__ == "__main__":
    create_product_mission(
        idea="Blueprint demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase52_runner"
    )

    result = generate_blueprint_from_latest_mission()

    print(json.dumps({
        "status": "PHASE52_PRODUCT_BLUEPRINT_GENERATED",
        "result_status": result.get("status"),
        "blueprint_id": result.get("blueprint", {}).get("blueprint_id"),
        "title": result.get("blueprint", {}).get("title"),
        "product_type": result.get("blueprint", {}).get("product_type"),
        "summary": summarize_blueprints(limit=10),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission, save_blueprint, summarize_blueprints

st.set_page_config(page_title="KOS Product Blueprint Generator", layout="wide")

st.title("KOS Product Factory Blueprint Generator")
st.caption("Gera blueprint completo a partir de uma missao de produto. Design-only.")

idea = st.text_input("Ideia", "Criar um SaaS de automacao comercial com IA modular")
product_type = st.selectbox("Tipo", ["saas", "app", "landing_page", "campaign", "automation", "api", "agent", "dashboard", "integration"])
target_user = st.text_input("Publico-alvo", "pequenos negocios")
market = st.text_input("Mercado", "automacao comercial")

mission = build_product_mission(
    idea=idea,
    product_type=product_type,
    target_user=target_user,
    market=market,
    priority="medium",
    source="streamlit_blueprint_draft"
)

blueprint = build_blueprint_from_mission(mission)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tipo", blueprint.get("product_type"))
col2.metric("Modulos", len(blueprint.get("architecture", {}).get("modules", [])))
col3.metric("Build", "BLOQUEADO")
col4.metric("Deploy", "BLOQUEADO")

st.subheader("Blueprint")
st.json(blueprint)

if st.button("Salvar blueprint local", use_container_width=True):
    saved = save_blueprint(blueprint)
    st.success("Blueprint salvo no runtime local.")
    st.json(saved)

st.subheader("Resumo")
st.json(summarize_blueprints(limit=20))

st.warning("Design-only. Sem build automatico, sem deploy, sem IA paga, sem Instagram.")
'''

test_code = r'''
from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission, save_blueprint, summarize_blueprints

def test_build_blueprint_is_safe():
    mission = build_product_mission(
        idea="SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )

    blueprint = build_blueprint_from_mission(mission)

    assert blueprint["status"] == "PRODUCT_BLUEPRINT_READY"
    assert blueprint["gates"]["execution_allowed"] is False
    assert blueprint["gates"]["build_allowed"] is False
    assert blueprint["gates"]["deploy_allowed"] is False
    assert blueprint["gates"]["paid_ai_allowed"] is False
    assert blueprint["gates"]["instagram_publish_allowed"] is False
    assert blueprint["real_action_executed"] is False
    assert blueprint["paid_ai_call_executed"] is False
    assert blueprint["instagram_publish_executed"] is False
    assert blueprint["external_side_effects_executed"] is False

def test_blueprint_contains_required_sections():
    mission = build_product_mission(
        idea="Landing page teste",
        product_type="landing_page",
        target_user="lead",
        market="marketing"
    )

    blueprint = build_blueprint_from_mission(mission)

    assert "product_brief" in blueprint
    assert "mvp_scope" in blueprint
    assert "architecture" in blueprint
    assert "automation_plan" in blueprint
    assert "launch_plan" in blueprint
    assert "risk_register" in blueprint
    assert "acceptance_criteria" in blueprint

def test_save_blueprint_and_summary_are_safe():
    mission = build_product_mission(
        idea="Dashboard teste",
        product_type="dashboard",
        target_user="operador",
        market="dados"
    )

    blueprint = build_blueprint_from_mission(mission)
    saved = save_blueprint(blueprint)
    summary = summarize_blueprints(limit=5)

    assert saved["status"] == "PRODUCT_BLUEPRINT_SAVED"
    assert summary["status"] == "PRODUCT_BLUEPRINT_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_product_blueprint_policy.json", policy)
write(ROOT / "k_atlas" / "product_factory" / "blueprint_generator.py", blueprint_code.strip() + "\n")

init_path = ROOT / "k_atlas" / "product_factory" / "__init__.py"
init_text = init_path.read_text(encoding="utf-8-sig") if init_path.exists() else ""
extra = "\nfrom .blueprint_generator import build_blueprint_from_mission, generate_blueprint_from_latest_mission, summarize_blueprints\n"
if "blueprint_generator" not in init_text:
    init_path.write_text(init_text.rstrip() + extra, encoding="utf-8")

write(ROOT / "scripts" / "run_phase52_product_blueprint_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Product_Blueprint_Generator.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase52_product_blueprint.py", test_code.strip() + "\n")

report = {
    "status": "PHASE52_PRODUCT_BLUEPRINT_GENERATOR_BOOTSTRAPPED",
    "phase": "52",
    "created_files": [
        "config/kos_product_blueprint_policy.json",
        "k_atlas/product_factory/blueprint_generator.py",
        "scripts/run_phase52_product_blueprint_demo.py",
        "pages/KOS_Product_Blueprint_Generator.py",
        "tests/test_phase52_product_blueprint.py"
    ],
    "modified_files": [
        "k_atlas/product_factory/__init__.py"
    ],
    "runtime_files": [
        "local_runtime/product_factory_blueprints/blueprints_index.jsonl",
        "local_runtime/product_factory_blueprints/latest_blueprint_summary.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE52_PRODUCT_BLUEPRINT_GENERATOR_BOOTSTRAP.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))