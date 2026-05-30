from __future__ import annotations

from typing import Any, Mapping


BLOCKED_FLAGS = [
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
    "apply_now",
    "execute_now",
]

BLOCKED_MARKERS = [
    "token=",
    "api_key=",
    "password=",
    "senha=",
    "secret=",
    "access_token=",
    "refresh_token=",
]

ALLOWED_SOURCE_STATUS = {
    "decided",
}

ALLOWED_DECISION = "approve_for_apply_package"


def validate_apply_package_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    notes = str(data.get("notes", ""))
    lowered = notes.lower()

    for marker in BLOCKED_MARKERS:
        if marker.lower() in lowered:
            reasons.append(f"blocked_secret_marker:{marker}")

    return {
        "ok": len(reasons) == 0,
        "status": "apply_package_request_allowed" if not reasons else "apply_package_request_blocked",
        "reasons": reasons or ["apply_package_request_allowed"],
    }


def is_review_approved_for_package(review: Mapping[str, Any]) -> bool:
    decision = review.get("decision", {}) if isinstance(review.get("decision"), dict) else {}

    return (
        review.get("status") in ALLOWED_SOURCE_STATUS
        and decision.get("decision") == ALLOWED_DECISION
        and decision.get("apply_package_enabled") is True
        and decision.get("real_execution_enabled") is not True
        and review.get("execution_enabled") is not True
        and review.get("real_execution_enabled") is not True
    )
