from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config" / "kos_work_order_route_registry.json"

DEFAULT_UNKNOWN_FILES = [
    {
        "path": "reports/KOS_LOCAL_WORK_ORDER_REVIEW_REQUIRED.json",
        "purpose": "Relatorio de revisao quando o escopo nao estiver claro.",
    }
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {
            "status": "ROUTE_REGISTRY_READ_ERROR",
            "error": str(exc),
            "path": str(path),
        }

def normalize_text(value: object) -> str:
    return str(value or "").lower().strip()

def load_work_order_route_registry() -> dict:
    payload = _read_json(REGISTRY_PATH)
    if not payload:
        return {
            "status": "ROUTE_REGISTRY_MISSING",
            "routes": [],
            "unknown_route": {
                "route_id": "unknown_review_required",
                "proposed_files": DEFAULT_UNKNOWN_FILES,
            },
        }
    return payload

def _scope_text(task: dict) -> str:
    title = normalize_text(task.get("title"))
    body = normalize_text(task.get("body"))
    area = normalize_text(task.get("area"))
    return f"{title}\n{body}\n{area}"

def _task_type(task: dict) -> str:
    classification = task.get("classification", {}) or {}
    return normalize_text(classification.get("task_type", "general_operation"))

def _route_matches(route: dict, task: dict) -> bool:
    scope = _scope_text(task)
    task_type = _task_type(task)

    task_types = [normalize_text(item) for item in route.get("task_types", []) or []]
    if task_type and task_type in task_types:
        return True

    terms = [normalize_text(item) for item in route.get("match_any", []) or []]
    return any(term and term in scope for term in terms)

def route_work_order_task(task: dict, registry: dict | None = None) -> dict:
    payload = registry or load_work_order_route_registry()
    routes = payload.get("routes", []) or []

    ordered = sorted(
        routes,
        key=lambda item: int(item.get("priority", 0)),
        reverse=True,
    )

    for route in ordered:
        if _route_matches(route, task):
            return {
                "status": "WORK_ORDER_ROUTE_MATCHED",
                "route_id": route.get("route_id"),
                "priority": route.get("priority"),
                "proposed_files": route.get("proposed_files", []) or DEFAULT_UNKNOWN_FILES,
                "matched_at": now(),
            }

    unknown = payload.get("unknown_route", {}) or {}
    return {
        "status": "WORK_ORDER_ROUTE_REVIEW_REQUIRED",
        "route_id": unknown.get("route_id", "unknown_review_required"),
        "priority": 0,
        "proposed_files": unknown.get("proposed_files", DEFAULT_UNKNOWN_FILES),
        "matched_at": now(),
    }

def proposed_files_for_task(task: dict, registry: dict | None = None) -> list[dict]:
    route = route_work_order_task(task, registry=registry)
    return route.get("proposed_files", []) or DEFAULT_UNKNOWN_FILES

def get_work_order_route_registry_status() -> dict:
    payload = load_work_order_route_registry()
    routes = payload.get("routes", []) or []

    return {
        "status": "WORK_ORDER_ROUTE_REGISTRY_READY",
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)).replace("\\", "/"),
        "routes_count": len(routes),
        "routes": [
            {
                "route_id": item.get("route_id"),
                "priority": item.get("priority"),
                "match_terms_count": len(item.get("match_any", []) or []),
                "task_types_count": len(item.get("task_types", []) or []),
                "proposed_files_count": len(item.get("proposed_files", []) or []),
            }
            for item in sorted(routes, key=lambda r: int(r.get("priority", 0)), reverse=True)
        ],
        "unknown_route_requires_review": True,
        "no_command_execution": True,
        "no_paid_ai": True,
        "no_instagram": True,
        "no_deploy": True,
        "created_at": now(),
    }
