from __future__ import annotations

from typing import Any, Mapping


BLOCKED_FLAGS = [
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
]


def validate_manual_rollback_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    if data.get("human_approved") is not True:
        reasons.append("human_approval_required")

    if data.get("rollback_mode") != "manual":
        reasons.append("manual_rollback_mode_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "manual_rollback_request_allowed" if not reasons else "manual_rollback_request_blocked",
        "reasons": reasons or ["manual_rollback_request_allowed"],
    }
