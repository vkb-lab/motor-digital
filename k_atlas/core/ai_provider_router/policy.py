from __future__ import annotations

from typing import Any, Mapping


ALLOWED_TASK_TYPES = {
    "text_reasoning",
    "agent_orchestration",
    "image_generation",
    "video_generation",
    "audio_generation",
    "social_caption",
    "saas_build",
    "deploy_analysis",
    "embedding",
    "multimodal_analysis",
}

ALLOWED_PROVIDERS = {
    "openai",
    "google_ai",
    "google_vertex",
    "local_stub",
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
    "live_call",
    "auto_publish",
    "official_publish",
    "auto_deploy",
    "mass_messaging",
    "browser_automation",
]


def validate_router_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    task_type = str(data.get("task_type", "")).strip()
    preferred_provider = str(data.get("preferred_provider", "")).strip()

    if task_type not in ALLOWED_TASK_TYPES:
        reasons.append(f"task_type_not_allowed:{task_type}")

    if preferred_provider and preferred_provider not in ALLOWED_PROVIDERS:
        reasons.append(f"provider_not_allowed:{preferred_provider}")

    for key in BLOCKED_KEYS:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "router_payload_allowed" if not reasons else "router_payload_blocked",
        "reasons": reasons or ["router_payload_allowed"],
    }
