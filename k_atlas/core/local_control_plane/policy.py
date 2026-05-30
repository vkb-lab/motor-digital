from __future__ import annotations

from typing import Any, Mapping


ALLOWED_MODES = {
    "observe",
    "list",
    "recommend",
    "lan_readiness",
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
    "remote_control_enabled",
    "public_internet_exposure",
    "open_firewall",
]


def validate_control_plane_request(payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    mode = data.get("mode", "observe")
    if mode not in ALLOWED_MODES:
        reasons.append(f"invalid_mode:{mode}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "control_plane_request_allowed" if not reasons else "control_plane_request_blocked",
        "mode": mode,
        "reasons": reasons or ["control_plane_request_allowed"],
        "execution_enabled": False,
        "real_execution_enabled": False,
        "external_side_effects": "none",
    }
