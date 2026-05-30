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


def validate_saas_product_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    product_name = str(data.get("product_name", "")).strip()
    audience = str(data.get("audience", "")).strip()
    problem = str(data.get("problem", "")).strip()

    if not product_name:
        reasons.append("product_name_required")

    if not audience:
        reasons.append("audience_required")

    if not problem:
        reasons.append("problem_required")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    for key in ["token", "api_key", "password", "secret"]:
        if data.get(key):
            reasons.append(f"plaintext_{key}_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "saas_product_allowed" if not reasons else "saas_product_blocked",
        "reasons": reasons or ["saas_product_payload_allowed"],
    }
