from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


ALLOWED_ACTIONS = {
    "create_module",
    "create_streamlit_page",
    "create_smoke_test",
    "create_ops_script",
    "create_readme",
    "update_gitignore",
    "create_report",
}

ALLOWED_PREFIXES = (
    "k_atlas/",
    "agents/",
    "pages/",
    "ops/",
    "README_",
    "tests/",
)

BLOCKED_CONTENT_MARKERS = (
    "token=",
    "api_key=",
    "password=",
    "senha=",
    "client_secret=",
    "access_token=",
    "refresh_token=",
    "auto_publish=true",
    "auto_send=true",
    "auto_deploy=true",
    "browser_automation=true",
    "mouse_automation=true",
    "eval(",
    "exec(",
    "subprocess.Popen",
    "os.system",
)

MAX_OBJECTIVE_SIZE = 5000
MAX_FILE_CONTENT_SIZE = 60000


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def validate_autoprog_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    objective = str(data.get("objective", "")).strip()
    checkpoint = str(data.get("checkpoint", "")).strip()
    action = str(data.get("action", "create_module")).strip()

    if not objective:
        reasons.append("objective_required")

    if len(objective) > MAX_OBJECTIVE_SIZE:
        reasons.append("objective_too_large")

    if not checkpoint:
        reasons.append("checkpoint_required")

    if action not in ALLOWED_ACTIONS:
        reasons.append(f"action_not_allowed:{action}")

    flags = {
        "real_execution_enabled": data.get("real_execution_enabled", False),
        "external_api_enabled": data.get("external_api_enabled", False),
        "auto_publish": data.get("auto_publish", False),
        "auto_send": data.get("auto_send", False),
        "auto_deploy": data.get("auto_deploy", False),
        "browser_automation": data.get("browser_automation", False),
        "mouse_automation": data.get("mouse_automation", False),
    }

    for key, value in flags.items():
        if value is True:
            reasons.append(f"{key}_blocked")

    lowered = objective.lower()

    for marker in BLOCKED_CONTENT_MARKERS:
        if marker.lower() in lowered:
            reasons.append(f"blocked_marker:{marker}")

    return {
        "ok": len(reasons) == 0,
        "status": "autoprog_request_allowed" if not reasons else "autoprog_request_blocked",
        "reasons": reasons or ["autoprog_request_allowed"],
        "checkpoint": checkpoint,
        "action": action,
    }


def validate_file_plan(file_plan: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(file_plan or {})
    reasons: list[str] = []

    path = normalize_path(str(data.get("path", "")))
    action = str(data.get("action", "create_module")).strip()
    content = str(data.get("content", ""))

    if not path:
        reasons.append("path_required")

    if Path(path).is_absolute():
        reasons.append("absolute_path_blocked")

    if ".." in Path(path).parts:
        reasons.append("parent_path_blocked")

    if not path.startswith(ALLOWED_PREFIXES):
        reasons.append(f"path_prefix_not_allowed:{path}")

    if action not in ALLOWED_ACTIONS:
        reasons.append(f"action_not_allowed:{action}")

    if len(content) > MAX_FILE_CONTENT_SIZE:
        reasons.append("content_too_large")

    lowered = content.lower()

    for marker in BLOCKED_CONTENT_MARKERS:
        if marker.lower() in lowered:
            reasons.append(f"blocked_marker:{marker}")

    return {
        "ok": len(reasons) == 0,
        "status": "file_plan_allowed" if not reasons else "file_plan_blocked",
        "reasons": reasons or ["file_plan_allowed"],
        "path": path,
        "action": action,
    }
