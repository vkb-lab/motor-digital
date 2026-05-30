from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping


ALLOWED_PREFIXES = (
    "k_atlas/",
    "agents/",
    "pages/",
    "ops/",
    "README_",
    "tests/",
    "content_packs/",
    "reports/autoprog_generated/",
)

ALLOWED_ACTIONS = {
    "write_file",
    "append_file",
}

BLOCKED_ACTIONS = {
    "run_shell",
    "powershell",
    "python_exec",
    "subprocess",
    "browser_automation",
    "mouse_automation",
    "api_call",
    "deploy",
    "publish",
    "send_message",
}

BLOCKED_FLAGS = [
    "auto_execute",
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
]

BLOCKED_MARKERS = [
    "token=",
    "api_key=",
    "password=",
    "senha=",
    "secret=",
    "access_token=",
    "refresh_token=",
    "client_secret=",
    "invoke-expression",
    "iex ",
    "subprocess.",
    "os.system",
    "start-process",
]

MAX_STEP_CONTENT_CHARS = 300000


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_path(value: str) -> str:
    return str(value or "").replace("\\", "/").strip()


def validate_safe_path(path_value: str) -> dict[str, Any]:
    path = normalize_path(path_value)
    reasons: list[str] = []

    if not path:
        reasons.append("path_required")

    if Path(path).is_absolute():
        reasons.append("absolute_path_blocked")

    if ".." in Path(path).parts:
        reasons.append("parent_path_blocked")

    if not path.startswith(ALLOWED_PREFIXES):
        reasons.append(f"path_prefix_not_allowed:{path}")

    return {
        "ok": len(reasons) == 0,
        "path": path,
        "reasons": reasons or ["path_allowed"],
    }


def validate_mission_step(step: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(step or {})
    reasons: list[str] = []

    action = str(data.get("action", "")).strip()
    if not action:
        reasons.append("action_required")
    elif action in BLOCKED_ACTIONS:
        reasons.append(f"blocked_action:{action}")
    elif action not in ALLOWED_ACTIONS:
        reasons.append(f"action_not_allowed:{action}")

    path_result = validate_safe_path(str(data.get("path", "")))
    if not path_result["ok"]:
        reasons.extend(path_result["reasons"])

    content = str(data.get("content", ""))
    if action in ALLOWED_ACTIONS and content == "":
        reasons.append("content_required")

    if len(content) > MAX_STEP_CONTENT_CHARS:
        reasons.append("content_too_large")

    expected_hash = str(data.get("content_sha256", "")).strip()
    actual_hash = sha256_text(content)

    if expected_hash and expected_hash != actual_hash:
        reasons.append("content_hash_mismatch")

    lowered = content.lower()
    for marker in BLOCKED_MARKERS:
        if marker in lowered:
            reasons.append(f"blocked_marker:{marker}")

    return {
        "ok": len(reasons) == 0,
        "status": "mission_step_allowed" if not reasons else "mission_step_blocked",
        "action": action,
        "path": path_result["path"],
        "content_sha256": actual_hash,
        "reasons": reasons or ["mission_step_allowed"],
    }


def validate_mission_package(package: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(package or {})
    reasons: list[str] = []

    if data.get("schema_version") != "k_atlas.local_mission.v1":
        reasons.append(f"invalid_schema_version:{data.get('schema_version')}")

    if not data.get("mission_id"):
        reasons.append("mission_id_required")

    if not data.get("mission_name"):
        reasons.append("mission_name_required")

    if data.get("status") != "draft_ready_for_local_review":
        reasons.append(f"invalid_status:{data.get('status')}")

    if data.get("install_mode") != "manual_only":
        reasons.append("manual_only_install_mode_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    steps = data.get("steps", [])
    if not isinstance(steps, list) or not steps:
        reasons.append("steps_required")

    step_results: list[dict[str, Any]] = []

    for step in steps if isinstance(steps, list) else []:
        result = validate_mission_step(step)
        step_results.append(result)
        if not result["ok"]:
            reasons.append("invalid_step_detected")

    return {
        "ok": len(reasons) == 0,
        "status": "mission_package_allowed" if not reasons else "mission_package_blocked",
        "mission_id": data.get("mission_id"),
        "mission_name": data.get("mission_name"),
        "reasons": reasons or ["mission_package_allowed"],
        "step_results": step_results,
        "automatic_execution_allowed": False,
        "human_approval_required": True,
    }


def validate_manual_install_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    if data.get("human_approved") is not True:
        reasons.append("human_approval_required")

    if data.get("install_mode") != "manual":
        reasons.append("manual_install_mode_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "manual_install_request_allowed" if not reasons else "manual_install_request_blocked",
        "reasons": reasons or ["manual_install_request_allowed"],
    }
