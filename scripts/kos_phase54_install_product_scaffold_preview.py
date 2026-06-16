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
    "phase": "54",
    "module": "K-OS Product Factory Scaffold Preview",
    "mode": "SCAFFOLD_PREVIEW_DRY_RUN_ONLY",
    "goal": "transformar build plans em previews de scaffold sem criar produto real",
    "blocked_actions": {
        "write_product_code_automatically": True,
        "create_product_files_without_approval": True,
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
        "preview_only": True,
        "human_approval_required_before_file_creation": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True
    },
    "created_at": now()
}

scaffold_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import uuid

ROOT = Path(__file__).resolve().parents[2]
BUILD_PLAN_INDEX = ROOT / "local_runtime" / "product_factory_build_plans" / "build_plans_index.jsonl"
SCAFFOLD_DIR = ROOT / "local_runtime" / "product_factory_scaffolds"
SCAFFOLD_INDEX = SCAFFOLD_DIR / "scaffold_previews_index.jsonl"
SUMMARY_PATH = SCAFFOLD_DIR / "latest_scaffold_preview_summary.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "product-scaffold"

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

def get_latest_build_plan() -> dict:
    index = _read_jsonl(BUILD_PLAN_INDEX)
    if not index:
        return {}

    latest = index[-1]
    path = latest.get("path")
    if not path:
        return {}

    return _read_json(ROOT / path)

def infer_file_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".json":
        return "json"
    if suffix == ".md":
        return "markdown"
    if suffix in {".txt", ".env"}:
        return "text"
    return "file"

def build_scaffold_preview_from_build_plan(build_plan: dict) -> dict:
    title = build_plan.get("title") or "Produto sem titulo"
    slug = build_plan.get("slug") or slugify(title)
    product_type = build_plan.get("product_type") or "saas"
    suggested_files = build_plan.get("suggested_files", []) or []

    directories = sorted({
        str(Path(item.get("path", "")).parent).replace("\\", "/")
        for item in suggested_files
        if item.get("path")
    })

    file_previews = []
    for item in suggested_files:
        file_path = item.get("path")
        if not file_path:
            continue

        file_previews.append({
            "path": file_path,
            "purpose": item.get("purpose", ""),
            "file_type": infer_file_type(file_path),
            "would_create": True,
            "content_status": "placeholder_preview_only",
            "execution_allowed": False
        })

    preview = {
        "status": "PRODUCT_SCAFFOLD_PREVIEW_READY",
        "scaffold_preview_id": "PFSP-" + uuid.uuid4().hex[:12].upper(),
        "source_build_plan_id": build_plan.get("build_plan_id"),
        "source_blueprint_id": build_plan.get("source_blueprint_id"),
        "source_mission_id": build_plan.get("source_mission_id"),
        "title": title,
        "slug": slug,
        "product_type": product_type,
        "execution_mode": "DRY_RUN_ONLY",
        "target_root": build_plan.get("target_root") or f"products/{slug}",
        "directories_preview": directories,
        "files_preview": file_previews,
        "dependencies_preview": [
            {"name": "python", "required": True},
            {"name": "streamlit", "required": product_type in ["saas", "app", "dashboard", "landing_page"]},
            {"name": "pytest", "required": True}
        ],
        "future_commands_preview": [
            {
                "label": "Criar scaffold futuro",
                "command": "python scripts\\run_phase55_product_scaffold_writer.py",
                "execution_allowed_now": False
            },
            {
                "label": "Rodar testes futuros do produto",
                "command": f"python -m pytest products/{slug}/tests -q",
                "execution_allowed_now": False
            }
        ],
        "approval_required": {
            "required": True,
            "confirmation_phrase_future": "YES_CREATE_PRODUCT_SCAFFOLD_LOCAL_ONLY",
            "reason": "Criacao de arquivos reais de produto precisa de aprovacao humana explicita."
        },
        "gates": {
            "write_product_files_allowed": False,
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

    return preview

def save_scaffold_preview(preview: dict) -> dict:
    SCAFFOLD_DIR.mkdir(parents=True, exist_ok=True)

    slug = preview.get("slug") or "product-scaffold"
    preview_id = preview.get("scaffold_preview_id") or "PFSP-UNKNOWN"
    path = SCAFFOLD_DIR / f"{slug}_{preview_id}.json"

    path.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")

    index_item = {
        "scaffold_preview_id": preview_id,
        "source_build_plan_id": preview.get("source_build_plan_id"),
        "title": preview.get("title"),
        "product_type": preview.get("product_type"),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "created_at": preview.get("created_at"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }

    with SCAFFOLD_INDEX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(index_item, ensure_ascii=False) + "\n")

    summary = summarize_scaffold_previews(limit=20)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "PRODUCT_SCAFFOLD_PREVIEW_SAVED",
        "scaffold_preview_id": preview_id,
        "path": index_item["path"],
        "index_item": index_item,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }

def generate_scaffold_preview_from_latest_build_plan() -> dict:
    build_plan = get_latest_build_plan()
    if not build_plan:
        return {
            "status": "NO_PRODUCT_BUILD_PLAN_FOUND",
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    preview = build_scaffold_preview_from_build_plan(build_plan)
    save_result = save_scaffold_preview(preview)

    return {
        "status": "PRODUCT_SCAFFOLD_PREVIEW_GENERATED_FROM_LATEST_BUILD_PLAN",
        "scaffold_preview": preview,
        "save_result": save_result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False
    }

def summarize_scaffold_previews(limit: int = 20) -> dict:
    entries = _read_jsonl(SCAFFOLD_INDEX)[-limit:]
    latest = entries[-1] if entries else {}

    by_type = {}
    for item in entries:
        ptype = item.get("product_type", "unknown")
        by_type[ptype] = by_type.get(ptype, 0) + 1

    return {
        "status": "PRODUCT_SCAFFOLD_PREVIEW_SUMMARY_READY",
        "index_exists": SCAFFOLD_INDEX.exists(),
        "index_path": str(SCAFFOLD_INDEX.relative_to(ROOT)).replace("\\", "/"),
        "entries_returned": len(entries),
        "latest_scaffold_preview_id": latest.get("scaffold_preview_id"),
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
from k_atlas.product_factory.build_plan import generate_build_plan_from_latest_blueprint
from k_atlas.product_factory.scaffold_preview import generate_scaffold_preview_from_latest_build_plan, summarize_scaffold_previews

if __name__ == "__main__":
    create_product_mission(
        idea="Scaffold preview demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase54_runner"
    )

    generate_blueprint_from_latest_mission()
    generate_build_plan_from_latest_blueprint()
    result = generate_scaffold_preview_from_latest_build_plan()

    print(json.dumps({
        "status": "PHASE54_PRODUCT_SCAFFOLD_PREVIEW_GENERATED",
        "result_status": result.get("status"),
        "scaffold_preview_id": result.get("scaffold_preview", {}).get("scaffold_preview_id"),
        "title": result.get("scaffold_preview", {}).get("title"),
        "product_type": result.get("scaffold_preview", {}).get("product_type"),
        "files_preview_count": len(result.get("scaffold_preview", {}).get("files_preview", [])),
        "summary": summarize_scaffold_previews(limit=10),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.product_factory.scaffold_preview import (
    get_latest_build_plan,
    build_scaffold_preview_from_build_plan,
    save_scaffold_preview,
    summarize_scaffold_previews,
)

st.set_page_config(page_title="KOS Product Scaffold Preview", layout="wide")

st.title("KOS Product Factory Scaffold Preview")
st.caption("Gera preview de scaffold a partir do build plan. Dry-run only.")

build_plan = get_latest_build_plan()

if not build_plan:
    st.warning("Nenhum build plan local encontrado ainda.")
else:
    preview = build_scaffold_preview_from_build_plan(build_plan)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", preview.get("product_type"))
    col2.metric("Arquivos", len(preview.get("files_preview", [])))
    col3.metric("Criar arquivos", "BLOQUEADO")
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Scaffold Preview")
    st.json(preview)

    if st.button("Salvar preview local", use_container_width=True):
        saved = save_scaffold_preview(preview)
        st.success("Scaffold preview salvo no runtime local.")
        st.json(saved)

st.subheader("Resumo")
st.json(summarize_scaffold_previews(limit=20))

st.warning("Dry-run only. Nao cria arquivos reais de produto, nao executa build, nao usa IA paga, nao publica.")
'''

test_code = r'''
from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint
from k_atlas.product_factory.scaffold_preview import build_scaffold_preview_from_build_plan, save_scaffold_preview, summarize_scaffold_previews

def test_scaffold_preview_is_safe():
    mission = build_product_mission(
        idea="SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    preview = build_scaffold_preview_from_build_plan(build_plan)

    assert preview["status"] == "PRODUCT_SCAFFOLD_PREVIEW_READY"
    assert preview["gates"]["write_product_files_allowed"] is False
    assert preview["gates"]["build_allowed"] is False
    assert preview["gates"]["deploy_allowed"] is False
    assert preview["gates"]["paid_ai_allowed"] is False
    assert preview["real_action_executed"] is False
    assert preview["paid_ai_call_executed"] is False
    assert preview["instagram_publish_executed"] is False
    assert preview["external_side_effects_executed"] is False

def test_scaffold_preview_has_files_and_directories():
    mission = build_product_mission(
        idea="API teste",
        product_type="api",
        target_user="dev",
        market="integracoes"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    preview = build_scaffold_preview_from_build_plan(build_plan)

    assert "directories_preview" in preview
    assert "files_preview" in preview
    assert len(preview["files_preview"]) >= 1
    assert all(item["execution_allowed"] is False for item in preview["files_preview"])

def test_save_scaffold_preview_and_summary_are_safe():
    mission = build_product_mission(
        idea="Dashboard teste",
        product_type="dashboard",
        target_user="operador",
        market="dados"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    preview = build_scaffold_preview_from_build_plan(build_plan)
    saved = save_scaffold_preview(preview)
    summary = summarize_scaffold_previews(limit=5)

    assert saved["status"] == "PRODUCT_SCAFFOLD_PREVIEW_SAVED"
    assert summary["status"] == "PRODUCT_SCAFFOLD_PREVIEW_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_product_scaffold_preview_policy.json", policy)
write(ROOT / "k_atlas" / "product_factory" / "scaffold_preview.py", scaffold_code.strip() + "\n")

init_path = ROOT / "k_atlas" / "product_factory" / "__init__.py"
init_text = init_path.read_text(encoding="utf-8-sig") if init_path.exists() else ""
extra = "\nfrom .scaffold_preview import build_scaffold_preview_from_build_plan, generate_scaffold_preview_from_latest_build_plan, summarize_scaffold_previews\n"
if "scaffold_preview" not in init_text:
    init_path.write_text(init_text.rstrip() + extra, encoding="utf-8")

write(ROOT / "scripts" / "run_phase54_product_scaffold_preview_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Product_Scaffold_Preview.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase54_product_scaffold_preview.py", test_code.strip() + "\n")

report = {
    "status": "PHASE54_PRODUCT_SCAFFOLD_PREVIEW_BOOTSTRAPPED",
    "phase": "54",
    "created_files": [
        "config/kos_product_scaffold_preview_policy.json",
        "k_atlas/product_factory/scaffold_preview.py",
        "scripts/run_phase54_product_scaffold_preview_demo.py",
        "pages/KOS_Product_Scaffold_Preview.py",
        "tests/test_phase54_product_scaffold_preview.py"
    ],
    "modified_files": [
        "k_atlas/product_factory/__init__.py"
    ],
    "runtime_files": [
        "local_runtime/product_factory_scaffolds/scaffold_previews_index.jsonl",
        "local_runtime/product_factory_scaffolds/latest_scaffold_preview_summary.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE54_PRODUCT_SCAFFOLD_PREVIEW_BOOTSTRAP.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))