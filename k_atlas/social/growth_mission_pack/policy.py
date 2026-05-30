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


def validate_social_growth_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    brand = str(data.get("brand", "")).strip()
    channel = str(data.get("channel", "")).strip()

    if not brand:
        reasons.append("brand_required")

    if channel not in {"instagram", "linkedin", "youtube", "tiktok", "multi_channel"}:
        reasons.append(f"channel_not_allowed:{channel}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in ["token", "api_key", "password", "secret"]:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "social_growth_allowed" if not reasons else "social_growth_blocked",
        "reasons": reasons or ["social_growth_payload_allowed"],
    }
