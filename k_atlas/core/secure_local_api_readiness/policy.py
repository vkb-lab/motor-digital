from __future__ import annotations

from typing import Any, Mapping


BLOCKED_FLAGS = [
    "public_exposure",
    "open_firewall",
    "bind_public_ip",
    "external_api_enabled",
    "auto_execute",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
]

ALLOWED_MODES = {"readiness", "observe", "plan"}
ALLOWED_BIND_ADDRESSES = {"127.0.0.1", "localhost", "0.0.0.0"}


def validate_local_api_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    mode = data.get("mode", "readiness")
    if mode not in ALLOWED_MODES:
        reasons.append(f"invalid_mode:{mode}")

    bind = str(data.get("bind_address", "127.0.0.1"))
    if bind not in ALLOWED_BIND_ADDRESSES:
        reasons.append(f"bind_address_not_allowed:{bind}")

    if bind == "0.0.0.0" and data.get("human_approved_lan") is not True:
        reasons.append("lan_bind_requires_human_approval")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "local_api_request_allowed" if not reasons else "local_api_request_blocked",
        "reasons": reasons or ["local_api_request_allowed"],
    }
