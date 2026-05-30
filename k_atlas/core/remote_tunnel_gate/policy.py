from __future__ import annotations

from typing import Any, Mapping


ALLOWED_PROVIDERS = {"manual", "tailscale", "cloudflare", "ngrok", "vpn"}
BLOCKED_FLAGS = [
    "start_tunnel",
    "public_exposure",
    "store_token",
    "external_api_enabled",
    "auto_execute",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
]


def validate_tunnel_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    provider = data.get("provider", "manual")
    if provider not in ALLOWED_PROVIDERS:
        reasons.append(f"provider_not_allowed:{provider}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "tunnel_request_allowed_for_review" if not reasons else "tunnel_request_blocked",
        "reasons": reasons or ["tunnel_request_allowed_for_review"],
    }
