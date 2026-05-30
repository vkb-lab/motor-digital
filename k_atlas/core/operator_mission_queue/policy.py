from __future__ import annotations

from typing import Any, Mapping


ALLOWED_LAYERS = {
    "core",
    "social",
    "saas",
    "external",
    "ops",
    "creative",
    "growth",
}

ALLOWED_PRIORITY = {
    "low",
    "medium",
    "high",
    "critical",
}

ALLOWED_RISK = {
    "low",
    "medium",
    "high",
    "critical",
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


def validate_operator_mission_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    title = str(data.get("title", "")).strip()
    objective = str(data.get("objective", "")).strip()
    layer = str(data.get("layer", "")).strip()
    priority = str(data.get("priority", "medium")).strip()
    risk = str(data.get("risk", "medium")).strip()

    if not title:
        reasons.append("title_required")

    if not objective:
        reasons.append("objective_required")

    if layer not in ALLOWED_LAYERS:
        reasons.append(f"layer_not_allowed:{layer}")

    if priority not in ALLOWED_PRIORITY:
        reasons.append(f"priority_not_allowed:{priority}")

    if risk not in ALLOWED_RISK:
        reasons.append(f"risk_not_allowed:{risk}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "operator_mission_payload_allowed" if not reasons else "operator_mission_payload_blocked",
        "reasons": reasons or ["operator_mission_payload_allowed"],
    }
