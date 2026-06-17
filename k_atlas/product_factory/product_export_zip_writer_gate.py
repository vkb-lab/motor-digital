from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import zipfile

from k_atlas.product_factory.product_export_packager import (
    refresh_product_export_packager,
    get_latest_product_export_packager_report,
    BLOCKED_NAMES,
    BLOCKED_PARTS,
    BLOCKED_KEYWORDS,
)

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "local_runtime" / "product_export_zip_writer"
EXPORTS_DIR = RUNTIME_DIR / "exports"
LATEST_REPORT = RUNTIME_DIR / "latest_zip_writer_report.json"
EVENTS_PATH = RUNTIME_DIR / "zip_writer_events.jsonl"

CONFIRMATION_PHRASE = "YES_CREATE_PRODUCT_EXPORT_ZIP_LOCAL_ONLY"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _safe_rel(path: Path, root: Path | None = None) -> str:
    base = root or ROOT
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except Exception:
        return path.as_posix().replace("\\", "/")

def _is_sensitive_relative_path(value: str) -> tuple[bool, list[str]]:
    normalized = value.replace("\\", "/").lower()
    parts = set(normalized.split("/"))
    name = Path(normalized).name

    reasons = []

    if name in BLOCKED_NAMES:
        reasons.append("blocked_sensitive_filename")

    if any(part in BLOCKED_PARTS for part in parts):
        reasons.append("blocked_runtime_or_cache_path")

    if "memory/security" in normalized:
        reasons.append("blocked_memory_security_path")

    if any(keyword in name for keyword in BLOCKED_KEYWORDS):
        reasons.append("blocked_sensitive_keyword")

    return bool(reasons), reasons

def load_export_packager_report(refresh: bool = False) -> dict:
    if refresh:
        refresh_product_export_packager()
    return get_latest_product_export_packager_report()

def _extract_report(payload: dict) -> dict:
    return payload.get("report", payload)

def list_exportable_manifests(export_packager_payload: dict | None = None, refresh: bool = False) -> list[dict]:
    payload = export_packager_payload or load_export_packager_report(refresh=refresh)
    report = _extract_report(payload)
    return report.get("manifests", []) or []

def validate_manifest_for_zip(manifest: dict, root: Path | None = None) -> dict:
    base = root or ROOT
    slug = manifest.get("slug") or "unknown-product"
    allowed_files = manifest.get("allowed_files", []) or []
    blocked_files = manifest.get("blocked_files", []) or []

    validation_errors = []
    files_to_zip = []

    if manifest.get("status") != "PRODUCT_EXPORT_MANIFEST_READY":
        validation_errors.append("manifest_not_ready")

    if blocked_files:
        validation_errors.append("manifest_has_blocked_files")

    if not allowed_files:
        validation_errors.append("manifest_has_no_allowed_files")

    for item in allowed_files:
        rel_path = item.get("path") or ""
        rel_to_product = item.get("relative_to_product") or Path(rel_path).name

        sensitive, reasons = _is_sensitive_relative_path(rel_path)
        sensitive_product, product_reasons = _is_sensitive_relative_path(rel_to_product)

        if sensitive or sensitive_product:
            validation_errors.append({
                "error": "allowed_file_failed_sensitive_recheck",
                "path": rel_path,
                "reasons": reasons + product_reasons,
            })
            continue

        file_path = Path(rel_path)
        if not file_path.is_absolute():
            file_path = base / file_path

        if not file_path.exists() or not file_path.is_file():
            validation_errors.append({
                "error": "allowed_file_not_found",
                "path": rel_path,
            })
            continue

        files_to_zip.append({
            "source_path": _safe_rel(file_path, root=base),
            "arcname": rel_to_product.replace("\\", "/"),
            "size_bytes": file_path.stat().st_size,
        })

    ready = len(validation_errors) == 0 and len(files_to_zip) > 0

    return {
        "status": "PRODUCT_EXPORT_ZIP_VALIDATION_READY" if ready else "PRODUCT_EXPORT_ZIP_VALIDATION_BLOCKED",
        "slug": slug,
        "title": manifest.get("title"),
        "files_to_zip": files_to_zip,
        "files_to_zip_count": len(files_to_zip),
        "validation_errors": validation_errors,
        "zip_creation_allowed_now": False,
        "confirmation_required": CONFIRMATION_PHRASE,
        "gates": {
            "zip_creation_allowed_by_default": False,
            "zip_creation_requires_confirmation": True,
            "include_blocked_files": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

def build_zip_writer_gate_report(export_packager_payload: dict | None = None, refresh: bool = False, root: Path | None = None) -> dict:
    manifests = list_exportable_manifests(export_packager_payload=export_packager_payload, refresh=refresh)
    validations = [validate_manifest_for_zip(manifest, root=root) for manifest in manifests]

    ready = [item for item in validations if item.get("status") == "PRODUCT_EXPORT_ZIP_VALIDATION_READY"]
    blocked = [item for item in validations if item.get("status") != "PRODUCT_EXPORT_ZIP_VALIDATION_READY"]

    return {
        "status": "PRODUCT_EXPORT_ZIP_WRITER_GATE_REPORT_READY",
        "products_count": len(validations),
        "ready_for_zip_count": len(ready),
        "blocked_count": len(blocked),
        "validations": validations,
        "confirmation_required": CONFIRMATION_PHRASE,
        "output_dir": _safe_rel(EXPORTS_DIR),
        "gates": {
            "zip_creation_allowed_by_default": False,
            "zip_creation_allowed_only_with_confirmation": True,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "recommendations": [
            "Criar zip somente com confirmacao humana explicita.",
            "Usar apenas files_to_zip validados.",
            "Nunca incluir arquivos bloqueados, .env, tokens, credentials, local_runtime, logs ou memory/security.",
            "Nao fazer deploy automatico apos criar zip."
        ],
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

def save_zip_writer_report(report: dict) -> dict:
    payload = {
        "status": "PRODUCT_EXPORT_ZIP_WRITER_REPORT_SAVED",
        "report": report,
        "real_action_executed": report.get("real_action_executed", False),
        "zip_created": report.get("zip_created", False),
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    _write_json(LATEST_REPORT, payload)
    _append_jsonl(EVENTS_PATH, payload)
    return payload

def refresh_product_export_zip_writer_gate() -> dict:
    report = build_zip_writer_gate_report(refresh=True)
    saved = save_zip_writer_report(report)

    return {
        "status": "PRODUCT_EXPORT_ZIP_WRITER_GATE_REFRESHED",
        "products_count": report.get("products_count", 0),
        "ready_for_zip_count": report.get("ready_for_zip_count", 0),
        "blocked_count": report.get("blocked_count", 0),
        "confirmation_required": CONFIRMATION_PHRASE,
        "zip_creation_allowed_now": False,
        "saved": saved.get("status"),
        "report_path": _safe_rel(LATEST_REPORT),
        "real_action_executed": False,
        "zip_created": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

def create_product_export_zip(
    product_slug: str,
    confirmation: str,
    export_packager_payload: dict | None = None,
    root: Path | None = None,
    output_dir: Path | None = None,
) -> dict:
    base = root or ROOT
    out_dir = output_dir or EXPORTS_DIR

    if confirmation != CONFIRMATION_PHRASE:
        report = {
            "status": "PRODUCT_EXPORT_ZIP_CREATION_BLOCKED",
            "reason": "missing_or_invalid_confirmation",
            "product_slug": product_slug,
            "confirmation_required": CONFIRMATION_PHRASE,
            "zip_created": False,
            "zip_path": None,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "external_side_effects_executed": False,
            "created_at": now(),
        }
        save_zip_writer_report(report)
        return report

    manifests = list_exportable_manifests(export_packager_payload=export_packager_payload, refresh=False)
    manifest = next((item for item in manifests if item.get("slug") == product_slug), None)

    if not manifest:
        report = {
            "status": "PRODUCT_EXPORT_ZIP_CREATION_BLOCKED",
            "reason": "product_manifest_not_found",
            "product_slug": product_slug,
            "zip_created": False,
            "zip_path": None,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "external_side_effects_executed": False,
            "created_at": now(),
        }
        save_zip_writer_report(report)
        return report

    validation = validate_manifest_for_zip(manifest, root=base)
    if validation.get("status") != "PRODUCT_EXPORT_ZIP_VALIDATION_READY":
        report = {
            "status": "PRODUCT_EXPORT_ZIP_CREATION_BLOCKED",
            "reason": "validation_failed",
            "product_slug": product_slug,
            "validation": validation,
            "zip_created": False,
            "zip_path": None,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "external_side_effects_executed": False,
            "created_at": now(),
        }
        save_zip_writer_report(report)
        return report

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{product_slug}_export_package.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in validation.get("files_to_zip", []):
            source = Path(item["source_path"])
            if not source.is_absolute():
                source = base / source
            zf.write(source, arcname=item["arcname"])

    report = {
        "status": "PRODUCT_EXPORT_ZIP_CREATED",
        "product_slug": product_slug,
        "zip_created": True,
        "zip_path": _safe_rel(zip_path, root=base),
        "files_count": validation.get("files_to_zip_count", 0),
        "files": validation.get("files_to_zip", []),
        "confirmation_used": CONFIRMATION_PHRASE,
        "gates": {
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "real_action_executed": True,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    save_zip_writer_report(report)
    return report

def get_latest_product_export_zip_writer_report() -> dict:
    if LATEST_REPORT.exists():
        return _read_json(LATEST_REPORT)
    return save_zip_writer_report(build_zip_writer_gate_report(refresh=False))

if __name__ == "__main__":
    print(json.dumps(refresh_product_export_zip_writer_gate(), ensure_ascii=False, indent=2))