from __future__ import annotations

from typing import Any, Mapping


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


def validate_external_action_execution_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    action_type = str(data.get("action_type", "")).strip()
    request_id = str(data.get("request_id", "")).strip()

    if action_type and action_type not in ALLOWED_ACTION_TYPES:
        reasons.append(f"action_type_not_allowed:{action_type}")

    if not request_id:
        reasons.append("request_id_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "external_action_stub_allowed" if not reasons else "external_action_stub_blocked",
        "reasons": reasons or ["external_action_stub_allowed"],
    }
