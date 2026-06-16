from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from k_atlas.product_factory.product_registry import refresh_product_registry, get_latest_registry

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "local_runtime" / "product_local_runner_gate"
LATEST_REPORT = RUNTIME_DIR / "latest_runner_gate_report.json"
EVENTS_PATH = RUNTIME_DIR / "runner_gate_events.jsonl"

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

def _resolve_product_path(product: dict, root: Path | None = None) -> Path:
    base = root or ROOT
    raw = str(product.get("path") or "").strip()
    if not raw:
        return base / "products" / str(product.get("slug") or "unknown-product")

    path = Path(raw)
    if path.is_absolute():
        return path
    return base / path

def _manual_command(label: str, command: str) -> dict:
    return {
        "label": label,
        "command": command,
        "execution_allowed_now": False,
        "requires_human_operator": True,
    }

def build_manual_runner_commands(product: dict, root: Path | None = None) -> list[dict]:
    product_path = _resolve_product_path(product, root=root)
    display_path = str(product.get("path") or product_path).replace("\\", "/")

    commands = [
        _manual_command(
            "Abrir pasta do produto manualmente",
            f'cd "{display_path}"'
        )
    ]

    app_py = product_path / "app.py"
    tests_dir = product_path / "tests"

    if app_py.exists():
        commands.append(
            _manual_command(
                "Rodar app Python manualmente se aprovado",
                f'python "{display_path}/app.py"'
            )
        )
        commands.append(
            _manual_command(
                "Rodar app Streamlit manualmente se aprovado",
                f'python -m streamlit run "{display_path}/app.py"'
            )
        )

    if tests_dir.exists():
        commands.append(
            _manual_command(
                "Rodar testes do produto manualmente se aprovado",
                f'python -m pytest "{display_path}/tests" -q'
            )
        )

    return commands

def evaluate_product_local_runner_gate(product: dict, root: Path | None = None) -> dict:
    product_path = _resolve_product_path(product, root=root)
    app_py = product_path / "app.py"
    tests_dir = product_path / "tests"

    has_app_py = app_py.exists()
    has_tests_dir = tests_dir.exists()
    safe = product.get("safe") is True

    attention = []
    if not safe:
        attention.append("product_registry_marked_not_safe")
    if not has_app_py:
        attention.append("app_py_not_found")
    if not has_tests_dir:
        attention.append("tests_folder_not_found")

    status = "PRODUCT_LOCAL_RUNNER_GATE_READY" if safe and (has_app_py or has_tests_dir) else "PRODUCT_LOCAL_RUNNER_GATE_ATTENTION_REQUIRED"

    return {
        "status": status,
        "product_id": product.get("product_id"),
        "slug": product.get("slug"),
        "title": product.get("title"),
        "product_type": product.get("product_type"),
        "path": product.get("path"),
        "safe": safe,
        "has_app_py": has_app_py,
        "has_tests_dir": has_tests_dir,
        "attention": attention,
        "manual_commands": build_manual_runner_commands(product, root=root),
        "gates": {
            "read_only": True,
            "manual_execution_only": True,
            "product_execution_allowed": False,
            "shell_execution_allowed": False,
            "run_streamlit_allowed_now": False,
            "run_pytest_allowed_now": False,
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
        "created_at": now()
    }

def build_product_local_runner_gate_report(registry_payload: dict, root: Path | None = None) -> dict:
    snapshot = registry_payload.get("snapshot", registry_payload)
    products = snapshot.get("products", []) or []

    items = [evaluate_product_local_runner_gate(product, root=root) for product in products]

    ready = [item for item in items if item.get("status") == "PRODUCT_LOCAL_RUNNER_GATE_READY"]
    attention = [item for item in items if item.get("status") != "PRODUCT_LOCAL_RUNNER_GATE_READY"]

    return {
        "status": "PRODUCT_LOCAL_RUNNER_GATE_REPORT_READY",
        "products_count": len(items),
        "ready_count": len(ready),
        "attention_required_count": len(attention),
        "items": items,
        "gates": {
            "read_only": True,
            "manual_execution_only": True,
            "product_execution_allowed": False,
            "shell_execution_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "recommendations": [
            "Executar produtos somente manualmente apos revisao humana.",
            "Rodar testes antes de qualquer execucao local prolongada.",
            "Nao usar credenciais reais em produtos locais.",
            "Manter deploy, IA paga e publicacao externa bloqueados."
        ],
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def save_product_local_runner_gate_report(report: dict) -> dict:
    payload = {
        "status": "PRODUCT_LOCAL_RUNNER_GATE_REPORT_SAVED",
        "report": report,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_REPORT, payload)
    _append_jsonl(EVENTS_PATH, payload)
    return payload

def refresh_product_local_runner_gate() -> dict:
    refresh_product_registry()
    registry = get_latest_registry()
    report = build_product_local_runner_gate_report(registry)
    saved = save_product_local_runner_gate_report(report)

    return {
        "status": "PRODUCT_LOCAL_RUNNER_GATE_REFRESHED",
        "products_count": report.get("products_count", 0),
        "ready_count": report.get("ready_count", 0),
        "attention_required_count": report.get("attention_required_count", 0),
        "saved": saved.get("status"),
        "report_path": str(LATEST_REPORT.relative_to(ROOT)).replace("\\", "/"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def get_latest_product_local_runner_gate_report() -> dict:
    if LATEST_REPORT.exists():
        return _read_json(LATEST_REPORT)
    return save_product_local_runner_gate_report(build_product_local_runner_gate_report(get_latest_registry()))

if __name__ == "__main__":
    print(json.dumps(refresh_product_local_runner_gate(), ensure_ascii=False, indent=2))