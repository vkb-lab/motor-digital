from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


ALLOWED_PREFIXES = (
    "k_atlas/",
    "agents/",
    "pages/",
    "ops/",
    "README_",
    "tests/",
    "reports/autoprog_generated/",
)

BLOCKED_FLAGS = [
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
]


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def validate_target_path(path_value: str) -> dict[str, Any]:
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


def validate_manual_apply_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    if data.get("human_approved") is not True:
        reasons.append("human_approval_required")

    if data.get("apply_mode") != "manual":
        reasons.append("manual_apply_mode_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    notes = str(data.get("notes", ""))
    lowered = notes.lower()

    for marker in BLOCKED_MARKERS:
        if marker.lower() in lowered:
            reasons.append(f"blocked_secret_marker:{marker}")

    return {
        "ok": len(reasons) == 0,
        "status": "manual_apply_request_allowed" if not reasons else "manual_apply_request_blocked",
        "reasons": reasons or ["manual_apply_request_allowed"],
    }
