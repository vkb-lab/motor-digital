from __future__ import annotations

from typing import Any, Mapping


ALLOWED_ACTION_TYPES = {
    "mission_install",
    "mission_pipeline_run",
    "dashboard_open",
    "local_api_readiness",
    "lan_readiness",
    "remote_tunnel_readiness",
    "manual_checkpoint",
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


def validate_approval_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    action_type = data.get("action_type")
    if action_type not in ALLOWED_ACTION_TYPES:
        reasons.append(f"action_type_not_allowed:{action_type}")

    if not data.get("title"):
        reasons.append("title_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "approval_request_allowed" if not reasons else "approval_request_blocked",
        "reasons": reasons or ["approval_request_allowed"],
    }
