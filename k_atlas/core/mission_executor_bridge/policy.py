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


def validate_execution_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    max_tasks = int(data.get("max_tasks", 10) or 10)

    if max_tasks < 1:
        reasons.append("max_tasks_too_low")

    if max_tasks > 25:
        reasons.append("max_tasks_too_high")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in ["token", "api_key", "password", "secret"]:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "execution_allowed" if not reasons else "execution_blocked",
        "reasons": reasons or ["mission_execution_allowed"],
    }
