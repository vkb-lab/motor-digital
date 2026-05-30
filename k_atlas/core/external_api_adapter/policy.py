from __future__ import annotations

from typing import Any, Mapping


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
    "live_call",
    "auto_publish",
    "official_publish",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
]

ALLOWED_PROVIDERS = {
    "openai",
    "google_ai",
    "google_vertex",
    "meta_graph",
    "instagram_graph",
    "whatsapp_cloud",
    "render",
    "github",
    "cloudflare",
}


def validate_external_api_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    provider = str(data.get("provider", "")).strip()

    if provider and provider not in ALLOWED_PROVIDERS:
        reasons.append(f"provider_not_allowed:{provider}")

    for key in BLOCKED_KEYS:
        value = data.get(key)
        if value:
            reasons.append(f"plaintext_{key}_blocked")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    env_vars = data.get("env_vars", [])
    if env_vars and not isinstance(env_vars, list):
        reasons.append("env_vars_must_be_list")

    if isinstance(env_vars, list):
        for item in env_vars:
            if not isinstance(item, str):
                reasons.append("env_var_name_must_be_string")
                continue

            if "=" in item:
                reasons.append("env_var_must_not_contain_value")

            if item.strip() != item or not item.strip():
                reasons.append("env_var_invalid_name")

    return {
        "ok": len(reasons) == 0,
        "status": "external_api_payload_allowed" if not reasons else "external_api_payload_blocked",
        "reasons": reasons or ["external_api_payload_allowed"],
    }
