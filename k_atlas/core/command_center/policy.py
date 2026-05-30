from __future__ import annotations

from typing import Any, Mapping


BLOCKED_FLAGS = [
    "official_publish",
    "auto_publish",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
    "external_api_enabled",
]

ALLOWED_ACTIONS = {
    "health_check",
    "generate_autoreport",
    "check_daemon",
    "check_git",
    "sandbox_creative_plan",
    "saas_factory_plan",
    "deploy_assisted_check",
}


def validate_command_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    action = str(data.get("action", "")).strip()

    if action not in ALLOWED_ACTIONS:
        reasons.append(f"action_not_allowed:{action}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in ["token", "api_key", "password", "secret"]:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "allowed" if not reasons else "blocked",
        "reasons": reasons or ["command_allowed"],
    }
