from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from k_atlas.product_factory.product_registry import refresh_product_registry, get_latest_registry

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_DIR = ROOT / "local_runtime" / "product_cockpit_launcher"
LATEST_SNAPSHOT = LAUNCHER_DIR / "latest_launcher_snapshot.json"
EVENTS_PATH = LAUNCHER_DIR / "launcher_events.jsonl"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def build_launch_instructions(product_record: dict) -> dict:
    slug = product_record.get("slug") or "unknown-product"
    path = product_record.get("path") or f"products/{slug}"
    has_tests = product_record.get("has_tests") is True

    commands = [
        {
            "label": "Abrir pasta do produto manualmente",
            "command": f"cd {path}",
            "execution_allowed_now": False
        },
        {
            "label": "Executar app Streamlit manualmente se existir",
            "command": f"streamlit run {path}/app.py",
            "execution_allowed_now": False
        },
        {
            "label": "Executar app Python manualmente se existir",
            "command": f"python {path}/app.py",
            "execution_allowed_now": False
        }
    ]

    if has_tests:
        commands.append({
            "label": "Rodar testes do produto manualmente",
            "command": f"python -m pytest {path}/tests -q",
            "execution_allowed_now": False
        })

    return {
        "status": "PRODUCT_LAUNCH_INSTRUCTIONS_READY",
        "product_id": product_record.get("product_id"),
        "slug": slug,
        "title": product_record.get("title"),
        "product_type": product_record.get("product_type"),
        "path": path,
        "safe": product_record.get("safe") is True,
        "attention_required": product_record.get("safe") is not True,
        "commands": commands,
        "notes": [
            "Estas instrucoes sao somente leitura.",
            "O K-OS nao executa estes comandos automaticamente.",
            "Executar produto local exige decisao humana.",
            "Deploy permanece bloqueado."
        ],
        "gates": {
            "shell_execution_allowed": False,
            "product_execution_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_operator_required": True
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def build_launcher_snapshot(registry_payload: dict) -> dict:
    snapshot = registry_payload.get("snapshot", registry_payload)
    products = snapshot.get("products", []) or []
    launch_items = [build_launch_instructions(item) for item in products]

    return {
        "status": "PRODUCT_COCKPIT_LAUNCHER_READY",
        "products_count": len(launch_items),
        "safe_products_count": len([item for item in launch_items if item.get("safe") is True]),
        "attention_required_count": len([item for item in launch_items if item.get("attention_required") is True]),
        "launch_items": launch_items,
        "gates": {
            "read_only": True,
            "shell_execution_allowed": False,
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

def save_launcher_snapshot(snapshot: dict) -> dict:
    payload = {
        "status": "PRODUCT_COCKPIT_LAUNCHER_SAVED",
        "snapshot": snapshot,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_SNAPSHOT, payload)
    _append_jsonl(EVENTS_PATH, payload)
    return payload

def refresh_product_cockpit_launcher() -> dict:
    refresh_product_registry()
    registry = get_latest_registry()
    snapshot = build_launcher_snapshot(registry)
    saved = save_launcher_snapshot(snapshot)

    return {
        "status": "PRODUCT_COCKPIT_LAUNCHER_REFRESHED",
        "products_count": snapshot.get("products_count", 0),
        "safe_products_count": snapshot.get("safe_products_count", 0),
        "attention_required_count": snapshot.get("attention_required_count", 0),
        "saved": saved.get("status"),
        "launcher_path": str(LATEST_SNAPSHOT.relative_to(ROOT)).replace("\\", "/"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def get_latest_launcher_snapshot() -> dict:
    if LATEST_SNAPSHOT.exists():
        return _read_json(LATEST_SNAPSHOT)
    snapshot = build_launcher_snapshot(get_latest_registry())
    return save_launcher_snapshot(snapshot)

if __name__ == "__main__":
    print(json.dumps(refresh_product_cockpit_launcher(), ensure_ascii=False, indent=2))