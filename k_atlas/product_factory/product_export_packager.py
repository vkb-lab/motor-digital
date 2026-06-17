from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from k_atlas.product_factory.product_registry import refresh_product_registry, get_latest_registry
from k_atlas.product_factory.product_local_runner_gate import refresh_product_local_runner_gate, get_latest_product_local_runner_gate_report

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "local_runtime" / "product_export_packager"
LATEST_REPORT = RUNTIME_DIR / "latest_export_packager_report.json"
EVENTS_PATH = RUNTIME_DIR / "export_packager_events.jsonl"

BLOCKED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "secrets.json",
    "credentials.json",
    "token.json",
    "tokens.json",
    "service-account.json",
}

BLOCKED_PARTS = {
    "local_runtime",
    "logs",
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "venv",
}

BLOCKED_SECURITY_PARTS = {
    "memory/security",
    "memory\\security",
}

BLOCKED_KEYWORDS = {
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
    "tokens",
    "private_key",
    "apikey",
    "api_key",
}

ALLOWED_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".csv",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".webp",
}

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

def _resolve_product_path(product: dict, root: Path | None = None) -> Path:
    base = root or ROOT
    raw = str(product.get("path") or "").strip()
    if raw:
        path = Path(raw)
        if path.is_absolute():
            return path
        return base / path
    return base / "products" / str(product.get("slug") or "unknown-product")

def _is_blocked_file(path: Path, product_path: Path) -> tuple[bool, list[str]]:
    reasons = []
    name = path.name.lower()
    rel = path.relative_to(product_path).as_posix().lower()
    parts = {part.lower() for part in path.relative_to(product_path).parts}

    if name in BLOCKED_NAMES:
        reasons.append("blocked_sensitive_filename")

    if any(part in BLOCKED_PARTS for part in parts):
        reasons.append("blocked_runtime_or_cache_path")

    if any(blocked in rel for blocked in BLOCKED_SECURITY_PARTS):
        reasons.append("blocked_memory_security_path")

    if any(keyword in name for keyword in BLOCKED_KEYWORDS):
        reasons.append("blocked_sensitive_keyword")

    if path.suffix.lower() and path.suffix.lower() not in ALLOWED_SUFFIXES:
        reasons.append("suffix_not_in_allowed_export_list")

    return bool(reasons), reasons

def scan_product_export_files(product: dict, root: Path | None = None) -> dict:
    product_path = _resolve_product_path(product, root=root)

    if not product_path.exists() or not product_path.is_dir():
        return {
            "status": "PRODUCT_EXPORT_SCAN_ATTENTION_REQUIRED",
            "product_path": _safe_rel(product_path, root=root),
            "allowed_files": [],
            "blocked_files": [],
            "attention": ["product_path_not_found"],
        }

    allowed_files = []
    blocked_files = []

    for path in sorted(product_path.rglob("*")):
        if not path.is_file():
            continue

        blocked, reasons = _is_blocked_file(path, product_path)

        item = {
            "path": _safe_rel(path, root=root),
            "relative_to_product": path.relative_to(product_path).as_posix(),
            "size_bytes": path.stat().st_size,
        }

        if blocked:
            item["blocked_reasons"] = reasons
            blocked_files.append(item)
        else:
            allowed_files.append(item)

    attention = []
    if blocked_files:
        attention.append("blocked_files_detected")
    if not allowed_files:
        attention.append("no_allowed_files_detected")

    return {
        "status": "PRODUCT_EXPORT_SCAN_READY" if allowed_files else "PRODUCT_EXPORT_SCAN_ATTENTION_REQUIRED",
        "product_path": _safe_rel(product_path, root=root),
        "allowed_files": allowed_files,
        "blocked_files": blocked_files,
        "attention": attention,
    }

def find_latest_qa_gate_snapshot(root: Path | None = None) -> dict:
    base = root or ROOT
    candidates = [
        base / "local_runtime" / "product_qa_gate" / "latest_product_qa_gate_report.json",
        base / "local_runtime" / "product_qa_gate" / "latest_qa_gate_report.json",
        base / "reports" / "KOS_PHASE59_PRODUCT_QA_GATE_REPORT.json",
    ]

    for path in candidates:
        if path.exists():
            return {
                "status": "QA_GATE_SNAPSHOT_FOUND",
                "path": _safe_rel(path, root=base),
                "payload": _read_json(path),
            }

    matches = sorted((base / "local_runtime").glob("**/*qa*gate*.json")) if (base / "local_runtime").exists() else []
    if matches:
        path = matches[-1]
        return {
            "status": "QA_GATE_SNAPSHOT_FOUND_BY_SEARCH",
            "path": _safe_rel(path, root=base),
            "payload": _read_json(path),
        }

    return {
        "status": "QA_GATE_SNAPSHOT_NOT_FOUND",
        "path": None,
        "payload": {},
    }

def build_product_export_manifest(product: dict, root: Path | None = None) -> dict:
    scan = scan_product_export_files(product, root=root)

    slug = product.get("slug") or "unknown-product"
    safe = product.get("safe") is True

    attention = list(scan.get("attention", []))
    if not safe:
        attention.append("product_registry_marked_not_safe")

    manifest = {
        "status": "PRODUCT_EXPORT_MANIFEST_READY" if safe and scan.get("allowed_files") else "PRODUCT_EXPORT_MANIFEST_ATTENTION_REQUIRED",
        "product_id": product.get("product_id"),
        "slug": slug,
        "title": product.get("title"),
        "product_type": product.get("product_type"),
        "path": product.get("path"),
        "safe": safe,
        "allowed_files_count": len(scan.get("allowed_files", [])),
        "blocked_files_count": len(scan.get("blocked_files", [])),
        "allowed_files": scan.get("allowed_files", []),
        "blocked_files": scan.get("blocked_files", []),
        "attention": attention,
        "future_zip_plan": {
            "zip_creation_allowed_now": False,
            "suggested_zip_name": f"{slug}_export_package.zip",
            "source_product_path": scan.get("product_path"),
            "include_allowed_files_only": True,
            "exclude_blocked_files": True,
            "requires_human_review": True,
        },
        "manual_commands_preview": [
            {
                "label": "Revisar manifesto antes de empacotar",
                "command": "Abrir Product Export Packager no cockpit e revisar allowed_files e blocked_files.",
                "execution_allowed_now": False,
            },
            {
                "label": "Criar zip futuro somente apos gate humano",
                "command": f"Comando futuro bloqueado: criar zip {slug}_export_package.zip",
                "execution_allowed_now": False,
            },
        ],
        "gates": {
            "read_only": True,
            "package_creation_allowed": False,
            "zip_creation_allowed": False,
            "copy_files_allowed": False,
            "shell_execution_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    return manifest

def build_product_export_packager_report(registry_payload: dict, qa_snapshot: dict | None = None, runner_snapshot: dict | None = None, root: Path | None = None) -> dict:
    snapshot = registry_payload.get("snapshot", registry_payload)
    products = snapshot.get("products", []) or []

    manifests = [build_product_export_manifest(product, root=root) for product in products]

    ready = [item for item in manifests if item.get("status") == "PRODUCT_EXPORT_MANIFEST_READY"]
    attention = [item for item in manifests if item.get("status") != "PRODUCT_EXPORT_MANIFEST_READY"]

    return {
        "status": "PRODUCT_EXPORT_PACKAGER_REPORT_READY",
        "products_count": len(manifests),
        "ready_count": len(ready),
        "attention_required_count": len(attention),
        "qa_gate_snapshot": qa_snapshot or {},
        "runner_gate_snapshot": runner_snapshot or {},
        "manifests": manifests,
        "global_blocklist": {
            "blocked_names": sorted(BLOCKED_NAMES),
            "blocked_parts": sorted(BLOCKED_PARTS),
            "blocked_keywords": sorted(BLOCKED_KEYWORDS),
            "allowed_suffixes": sorted(ALLOWED_SUFFIXES),
        },
        "gates": {
            "read_only": True,
            "package_creation_allowed": False,
            "zip_creation_allowed": False,
            "copy_files_allowed": False,
            "shell_execution_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "recommendations": [
            "Revisar blocked_files antes de qualquer exportacao.",
            "Criar zip somente em fase futura com gate humano explicito.",
            "Nunca incluir .env, tokens, credentials, local_runtime, logs ou memory/security.",
            "Executar QA Gate e Runner Gate antes de qualquer pacote exportavel real."
        ],
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

def save_product_export_packager_report(report: dict) -> dict:
    payload = {
        "status": "PRODUCT_EXPORT_PACKAGER_REPORT_SAVED",
        "report": report,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    _write_json(LATEST_REPORT, payload)
    _append_jsonl(EVENTS_PATH, payload)
    return payload

def refresh_product_export_packager() -> dict:
    refresh_product_registry()
    registry = get_latest_registry()

    qa_snapshot = find_latest_qa_gate_snapshot()

    try:
        refresh_product_local_runner_gate()
        runner_snapshot = get_latest_product_local_runner_gate_report()
    except Exception as exc:
        runner_snapshot = {
            "status": "RUNNER_GATE_SNAPSHOT_ERROR",
            "error": str(exc),
        }

    report = build_product_export_packager_report(
        registry_payload=registry,
        qa_snapshot=qa_snapshot,
        runner_snapshot=runner_snapshot,
    )

    saved = save_product_export_packager_report(report)

    return {
        "status": "PRODUCT_EXPORT_PACKAGER_REFRESHED",
        "products_count": report.get("products_count", 0),
        "ready_count": report.get("ready_count", 0),
        "attention_required_count": report.get("attention_required_count", 0),
        "saved": saved.get("status"),
        "report_path": _safe_rel(LATEST_REPORT),
        "package_creation_allowed": False,
        "zip_creation_allowed": False,
        "deploy_allowed": False,
        "paid_ai_allowed": False,
        "instagram_publish_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

def get_latest_product_export_packager_report() -> dict:
    if LATEST_REPORT.exists():
        return _read_json(LATEST_REPORT)

    registry = get_latest_registry()
    report = build_product_export_packager_report(
        registry_payload=registry,
        qa_snapshot=find_latest_qa_gate_snapshot(),
        runner_snapshot=get_latest_product_local_runner_gate_report(),
    )
    return save_product_export_packager_report(report)

if __name__ == "__main__":
    print(json.dumps(refresh_product_export_packager(), ensure_ascii=False, indent=2))