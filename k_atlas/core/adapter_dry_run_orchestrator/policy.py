from __future__ import annotations

from typing import Any, Mapping


ALLOWED_SCOPE = {
    "all",
    "instagram",
    "whatsapp",
    "render",
    "github",
    "openai",
    "google",
    "meta",
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


def validate_adapter_dry_run_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    scope = str(data.get("scope", "all")).strip()

    if scope not in ALLOWED_SCOPE:
        reasons.append(f"scope_not_allowed:{scope}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "adapter_dry_run_payload_allowed" if not reasons else "adapter_dry_run_payload_blocked",
        "reasons": reasons or ["adapter_dry_run_payload_allowed"],
    }
