from __future__ import annotations

from typing import Any


def validate_instagram_official_payload(payload: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []

    if payload.get("official_publish") is True:
        reasons.append("official_publish_blocked_until_level_4")

    if payload.get("auto_publish") is True:
        reasons.append("auto_publish_blocked")

    if payload.get("external_api_enabled") is True and not payload.get("credential_vault_ref"):
        reasons.append("external_api_requires_credential_vault")

    if payload.get("mass_messaging") is True:
        reasons.append("mass_messaging_blocked")

    if payload.get("browser_automation") is True:
        reasons.append("browser_automation_blocked_for_official_channel")

    return {
        "ok": len(reasons) == 0,
        "reasons": reasons or ["payload_allowed_for_planning"],
        "mode": "planning_only",
    }