from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD_INDEX = ROOT / "local_runtime" / "product_factory_scaffolds" / "scaffold_previews_index.jsonl"
REPORT_DIR = ROOT / "reports" / "product_factory_scaffold_writer"
LATEST_REPORT = REPORT_DIR / "latest_scaffold_writer_report.json"

CONFIRMATION_PHRASE = "YES_CREATE_PRODUCT_SCAFFOLD_LOCAL_ONLY"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

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

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_latest_scaffold_preview() -> dict:
    index = _read_jsonl(SCAFFOLD_INDEX)
    if not index:
        return {}
    latest = index[-1]
    rel_path = latest.get("path")
    if not rel_path:
        return {}
    return _read_json(ROOT / rel_path)

def _safe_relative_path(path_value: str) -> Path:
    raw = (path_value or "").replace("\\", "/").strip()
    if not raw:
        raise ValueError("path vazio")
    path = Path(raw)
    if path.is_absolute():
        raise ValueError("path absoluto bloqueado")
    if any(part in {"..", "", ".", "~"} for part in path.parts):
        raise ValueError("path inseguro bloqueado")
    if not raw.startswith("products/"):
        raise ValueError("path fora de products/ bloqueado")
    return path

def placeholder_content(file_path: str, purpose: str, product_title: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".md":
        return "\n".join([
            f"# {product_title}",
            "",
            "Arquivo scaffold gerado localmente pelo K-OS Product Factory.",
            "",
            "## Proposito",
            "",
            purpose,
            "",
            "## Garantias",
            "",
            "- Sem segredos.",
            "- Sem deploy automatico.",
            "- Sem IA paga.",
            "- Sem publicacao externa.",
            "- Revisao humana obrigatoria para evolucao.",
            ""
        ])

    if suffix == ".json":
        return json.dumps({
            "status": "SCAFFOLD_PLACEHOLDER",
            "product_title": product_title,
            "purpose": purpose,
            "secrets_included": False,
            "deploy_enabled": False,
            "paid_ai_enabled": False,
            "external_publish_enabled": False,
            "created_at": now()
        }, ensure_ascii=False, indent=2)

    if suffix == ".py":
        return "\n".join([
            '"""',
            "Scaffold placeholder gerado pelo K-OS Product Factory.",
            "",
            "Garantias:",
            "- Sem segredos.",
            "- Sem chamadas externas.",
            "- Sem IA paga.",
            "- Sem deploy.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "",
            "def get_status() -> dict:",
            "    return {",
            '        "status": "SCAFFOLD_PLACEHOLDER_READY",',
            f'        "purpose": {purpose!r},',
            '        "real_action_executed": False,',
            '        "paid_ai_call_executed": False,',
            '        "external_publish_executed": False,',
            "    }",
            "",
            "",
            'if __name__ == "__main__":',
            "    print(get_status())",
            ""
        ])

    return "\n".join([
        "Scaffold placeholder gerado pelo K-OS Product Factory.",
        "",
        f"Produto: {product_title}",
        f"Proposito: {purpose}",
        "",
        "Sem segredos.",
        "Sem deploy.",
        "Sem IA paga.",
        "Sem publicacao externa.",
        ""
    ])

def build_scaffold_write_plan(scaffold_preview: dict) -> dict:
    files_preview = scaffold_preview.get("files_preview", []) or []
    directories_preview = scaffold_preview.get("directories_preview", []) or []

    planned_files = []
    blocked = []

    for item in files_preview:
        file_path = item.get("path", "")
        try:
            safe_path = _safe_relative_path(file_path)
            planned_files.append({
                "path": str(safe_path).replace("\\", "/"),
                "purpose": item.get("purpose", ""),
                "file_type": item.get("file_type", "file"),
                "would_write": True
            })
        except Exception as exc:
            blocked.append({"path": file_path, "reason": str(exc)})

    safe_dirs = []
    for directory in directories_preview:
        try:
            safe_dirs.append(str(_safe_relative_path(directory)).replace("\\", "/"))
        except Exception:
            pass

    return {
        "status": "PRODUCT_SCAFFOLD_WRITE_PLAN_READY",
        "source_scaffold_preview_id": scaffold_preview.get("scaffold_preview_id"),
        "title": scaffold_preview.get("title"),
        "slug": scaffold_preview.get("slug"),
        "product_type": scaffold_preview.get("product_type"),
        "target_root": scaffold_preview.get("target_root"),
        "directories": sorted(set(safe_dirs)),
        "files": planned_files,
        "blocked_paths": blocked,
        "requires_confirmation": CONFIRMATION_PHRASE,
        "write_allowed_without_confirmation": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def write_scaffold_from_preview(scaffold_preview: dict, confirmation: str, dry_run: bool = False) -> dict:
    plan = build_scaffold_write_plan(scaffold_preview)
    valid_confirmation = (confirmation or "").strip() == CONFIRMATION_PHRASE

    if dry_run or not valid_confirmation:
        report = {
            "status": "PRODUCT_SCAFFOLD_WRITE_DRY_RUN" if dry_run else "PRODUCT_SCAFFOLD_WRITE_BLOCKED",
            "confirmation_valid": valid_confirmation,
            "dry_run": dry_run,
            "plan": plan,
            "created_directories": [],
            "created_files": [],
            "blocked_paths": plan.get("blocked_paths", []),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "external_side_effects_executed": False,
            "created_at": now()
        }
        _write_json(LATEST_REPORT, report)
        return report

    created_dirs = []
    created_files = []
    product_title = scaffold_preview.get("title") or "Produto K-OS"

    for directory in plan.get("directories", []):
        target_dir = ROOT / directory
        target_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(directory)

    for item in plan.get("files", []):
        rel_path = item.get("path")
        target_file = ROOT / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        if target_file.exists():
            continue

        content = placeholder_content(
            file_path=rel_path,
            purpose=item.get("purpose", ""),
            product_title=product_title
        )
        target_file.write_text(content, encoding="utf-8")
        created_files.append(rel_path)

    report = {
        "status": "PRODUCT_SCAFFOLD_WRITTEN_LOCAL_ONLY",
        "confirmation_valid": True,
        "dry_run": False,
        "plan": plan,
        "created_directories": created_dirs,
        "created_files": created_files,
        "blocked_paths": plan.get("blocked_paths", []),
        "real_action_executed": True,
        "scope": "local_file_creation_only",
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_REPORT, report)
    return report

def run_latest_scaffold_writer(confirmation: str = "", dry_run: bool = True) -> dict:
    preview = get_latest_scaffold_preview()
    if not preview:
        report = {
            "status": "NO_PRODUCT_SCAFFOLD_PREVIEW_FOUND",
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }
        _write_json(LATEST_REPORT, report)
        return report

    return write_scaffold_from_preview(preview, confirmation=confirmation, dry_run=dry_run)

if __name__ == "__main__":
    print(json.dumps(run_latest_scaffold_writer(dry_run=True), ensure_ascii=False, indent=2))