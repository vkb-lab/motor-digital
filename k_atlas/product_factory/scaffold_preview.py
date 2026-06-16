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
