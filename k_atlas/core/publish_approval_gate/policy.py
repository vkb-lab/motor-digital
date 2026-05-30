from __future__ import annotations

from typing import Any, Mapping


ALLOWED_ACTION_TYPES = {
    "instagram_publish",
    "whatsapp_send",
    "render_deploy",
    "github_release",
    "external_api_call",
    "campaign_launch",
    "content_generation",
    "manual_review",
}

ALLOWED_CHANNELS = {
    "instagram",
    "whatsapp",
    "render",
    "github",
    "openai",
    "google",
    "meta",
    "k_atlas_internal",
}

BLOCKED_KEYS = [
    "token",
    "api_key",
    "secret",
    "password",
    "client_secret",
    "access_token",
    "refresh_token",
]

BLOCKED_FLAGS = [
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
    "bypass_human_approval",
]


def validate_publish_approval_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    action_type = str(data.get("action_type", "")).strip()
    channel = str(data.get("channel", "")).strip()
    title = str(data.get("title", "")).strip()
    objective = str(data.get("objective", "")).strip()

    if action_type not in ALLOWED_ACTION_TYPES:
        reasons.append(f"action_type_not_allowed:{action_type}")

    if channel not in ALLOWED_CHANNELS:
        reasons.append(f"channel_not_allowed:{channel}")

    if not title:
        reasons.append("title_required")

    if not objective:
        reasons.append("objective_required")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    if data.get("live_call") is True and data.get("human_approved") is not True:
        reasons.append("live_call_requires_human_approval")

    if data.get("official_publish") is True and data.get("human_approved") is not True:
        reasons.append("official_publish_requires_human_approval")

    return {
        "ok": len(reasons) == 0,
        "status": "approval_payload_allowed" if not reasons else "approval_payload_blocked",
        "reasons": reasons or ["approval_payload_allowed"],
    }
