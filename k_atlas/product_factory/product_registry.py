from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS_DIR = ROOT / "products"
REGISTRY_DIR = ROOT / "local_runtime" / "product_registry"
LATEST_REGISTRY = REGISTRY_DIR / "latest_product_registry.json"
EVENTS_PATH = REGISTRY_DIR / "product_registry_events.jsonl"

FORBIDDEN_FILE_NAMES = {
    ".env",
    "secrets.json",
    "secret.json",
    "credentials.json",
    "tokens.json",
    "token.json",
    "ig_runtime.env",
}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return path.as_posix()

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

def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]

def detect_product_type(product_dir: Path) -> str:
    policy_path = product_dir / "config" / "product_policy.json"
    policy = _read_json(policy_path)
    if policy.get("product_type"):
        return str(policy["product_type"])

    name = product_dir.name.lower()
    if "landing" in name:
        return "landing_page"
    if "dashboard" in name:
        return "dashboard"
    if "api" in name:
        return "api"
    return "unknown"

def scan_product_directory(product_dir: Path) -> dict:
    files = []
    suspicious_files = []

    if not product_dir.exists() or not product_dir.is_dir():
        return {
            "status": "PRODUCT_DIRECTORY_NOT_FOUND",
            "path": str(product_dir),
            "exists": False,
            "safe": False,
            "files_count": 0,
            "suspicious_files": []
        }

    for path in sorted(product_dir.rglob("*")):
        if not path.is_file():
            continue

        rel = str(path.relative_to(product_dir)).replace("\\", "/")
        files.append(rel)

        if path.name.lower() in FORBIDDEN_FILE_NAMES:
            suspicious_files.append(rel)

    record = {
        "status": "PRODUCT_RECORD_READY",
        "product_id": "KOS-PRODUCT-" + _fingerprint(str(product_dir.resolve())),
        "slug": product_dir.name,
        "title": product_dir.name.replace("-", " ").replace("_", " ").title(),
        "product_type": detect_product_type(product_dir),
        "path": _safe_rel(product_dir),
        "files_count": len(files),
        "has_readme": "README.md" in files,
        "has_tests": any(item.startswith("tests/") for item in files),
        "has_policy": "config/product_policy.json" in files,
        "suspicious_files": suspicious_files,
        "safe": len(suspicious_files) == 0,
        "execution_allowed": False,
        "deploy_allowed": False,
        "paid_ai_allowed": False,
        "instagram_publish_allowed": False,
        "external_publish_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    return record

def scan_products(products_dir: Path | None = None) -> dict:
    base = products_dir or PRODUCTS_DIR
    records = []

    if base.exists():
        for child in sorted(base.iterdir()):
            if child.is_dir():
                records.append(scan_product_directory(child))

    summary = {
        "status": "PRODUCT_RUNTIME_REGISTRY_READY",
        "products_dir": _safe_rel(base) if base.exists() and base.is_relative_to(ROOT) else str(base),
        "products_count": len(records),
        "safe_products_count": len([item for item in records if item.get("safe") is True]),
        "attention_required_count": len([item for item in records if item.get("safe") is not True]),
        "products": records,
        "gates": {
            "read_only": True,
            "product_execution_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    return summary

def save_registry_snapshot(snapshot: dict) -> dict:
    payload = {
        "status": "PRODUCT_RUNTIME_REGISTRY_SAVED",
        "snapshot": snapshot,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_REGISTRY, payload)
    _append_jsonl(EVENTS_PATH, payload)
    return payload

def refresh_product_registry() -> dict:
    snapshot = scan_products()
    saved = save_registry_snapshot(snapshot)

    return {
        "status": "PRODUCT_RUNTIME_REGISTRY_REFRESHED",
        "products_count": snapshot.get("products_count", 0),
        "safe_products_count": snapshot.get("safe_products_count", 0),
        "attention_required_count": snapshot.get("attention_required_count", 0),
        "saved": saved.get("status"),
        "registry_path": str(LATEST_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def get_latest_registry() -> dict:
    if LATEST_REGISTRY.exists():
        return _read_json(LATEST_REGISTRY)
    return save_registry_snapshot(scan_products())

if __name__ == "__main__":
    print(json.dumps(refresh_product_registry(), ensure_ascii=False, indent=2))