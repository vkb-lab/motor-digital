from __future__ import annotations

from typing import Any, Mapping


ALLOWED_SCOPE = {
    "all",
    "core",
    "social",
    "saas",
    "external",
    "ops",
    "creative",
    "growth",
}

BLOCKED_FLAGS = [
    "live_call",
    "real_execute",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
    "bypass_human_approval",
]

BLOCKED_KEYS = [
    "token",
    "api_key",
    "secret",
    "password",
    "client_secret",
    "access_token",
    "refresh_token",
]


def validate_planning_approval_packager_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    scope = str(data.get("scope", "all")).strip()
    limit = data.get("limit", 25)

    if scope not in ALLOWED_SCOPE:
        reasons.append(f"scope_not_allowed:{scope}")

    if not isinstance(limit, int):
        reasons.append("limit_must_be_int")
    elif limit < 1 or limit > 100:
        reasons.append("limit_out_of_range")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "planning_approval_packager_payload_allowed" if not reasons else "planning_approval_packager_payload_blocked",
        "reasons": reasons or ["planning_approval_packager_payload_allowed"],
    }
