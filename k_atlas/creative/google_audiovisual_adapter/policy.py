from __future__ import annotations

from typing import Any, Mapping


ALLOWED_FORMATS = {
    "hero_video",
    "instagram_reel",
    "youtube_short",
    "ad_video",
    "product_demo",
    "image_concept",
    "carousel_visual",
}

BLOCKED_FLAGS = [
    "live_call",
    "auto_publish",
    "official_publish",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
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


def validate_audiovisual_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    asset_format = str(data.get("asset_format", "")).strip()
    brand = str(data.get("brand", "")).strip()
    objective = str(data.get("objective", "")).strip()

    if asset_format not in ALLOWED_FORMATS:
        reasons.append(f"asset_format_not_allowed:{asset_format}")

    if not brand:
        reasons.append("brand_required")

    if not objective:
        reasons.append("objective_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "audiovisual_payload_allowed" if not reasons else "audiovisual_payload_blocked",
        "reasons": reasons or ["audiovisual_payload_allowed"],
    }
