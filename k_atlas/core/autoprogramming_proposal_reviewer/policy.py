from __future__ import annotations

from typing import Any, Mapping


ALLOWED_DECISIONS = {
    "approve_for_apply_package",
    "request_changes",
    "deny",
    "hold",
}

BLOCKED_FLAGS = [
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
]

BLOCKED_WORDS = [
    "token=",
    "api_key=",
    "password=",
    "senha=",
    "secret=",
    "access_token=",
    "refresh_token=",
]


def validate_review_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    decision = str(data.get("decision", "hold")).strip()

    if decision not in ALLOWED_DECISIONS:
        reasons.append(f"decision_not_allowed:{decision}")

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    notes = str(data.get("notes", ""))
    lowered = notes.lower()

    for word in BLOCKED_WORDS:
        if word.lower() in lowered:
            reasons.append(f"blocked_secret_marker:{word}")

    return {
        "ok": len(reasons) == 0,
        "status": "review_payload_allowed" if not reasons else "review_payload_blocked",
        "decision": decision,
        "reasons": reasons or ["review_payload_allowed"],
    }
