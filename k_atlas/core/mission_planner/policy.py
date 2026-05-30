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

ALLOWED_MISSION_TYPES = {
    "system_health",
    "growth_planning",
    "creative_media",
    "saas_build",
    "deploy_readiness",
    "daily_operator",
}


def validate_mission_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    title = str(data.get("title", "")).strip()
    mission_type = str(data.get("mission_type", "")).strip()

    if not title:
        reasons.append("title_required")

    if mission_type not in ALLOWED_MISSION_TYPES:
        reasons.append(f"mission_type_not_allowed:{mission_type}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in ["token", "api_key", "password", "secret"]:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "mission_allowed" if not reasons else "mission_blocked",
        "reasons": reasons or ["mission_payload_allowed"],
    }
