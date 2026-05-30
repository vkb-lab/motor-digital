from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping


ALLOWED_ACTIONS = {
    "write_file",
    "append_file",
    "create_directory",
}

ALLOWED_PREFIXES = (
    "reports/autoprog_generated/",
    "content_packs/",
    "campaigns/generated/",
    "k_atlas/generated/",
    "tests/generated/",
    "README_",
)

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
    "subprocess.popen",
    "os.system",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def path_allowed(path_value: str) -> dict[str, Any]:
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

    if action not in ALLOWED_ACTIONS:
        reasons.append(f"action_not_allowed:{action}")

    path_result = path_allowed(str(data.get("path", "")))
    if not path_result["ok"]:
        reasons.extend(path_result["reasons"])

    content = str(data.get("content", ""))
    expected_hash = str(data.get("content_sha256", "")).strip()
    actual_hash = sha256_text(content)

    if action in {"write_file", "append_file"} and not content:
        reasons.append("content_required")

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


def validate_mission_pack(pack: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(pack or {})
    reasons: list[str] = []

    if not data.get("mission_pack_id"):
        reasons.append("mission_pack_id_required")

    if not data.get("mission_id"):
        reasons.append("mission_id_required")

    if not data.get("objective"):
        reasons.append("objective_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    steps = data.get("steps", [])

    if not isinstance(steps, list) or not steps:
        reasons.append("steps_required")
        steps = []

    step_results = []

    for step in steps:
        result = validate_mission_step(step)
        step_results.append(result)

        if not result["ok"]:
            reasons.append("invalid_step_detected")

    return {
        "ok": len(reasons) == 0,
        "status": "mission_pack_allowed" if not reasons else "mission_pack_blocked",
        "mission_pack_id": data.get("mission_pack_id"),
        "mission_id": data.get("mission_id"),
        "reasons": reasons or ["mission_pack_allowed"],
        "step_results": step_results,
        "automatic_execution_allowed": False,
        "human_approval_required": True,
        "external_side_effects": "none",
    }
