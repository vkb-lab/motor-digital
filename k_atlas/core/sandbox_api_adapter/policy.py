from __future__ import annotations

from typing import Any, Mapping

from k_atlas.core.credential_vault.policy import validate_secret_payload


def validate_sandbox_api_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    secret_validation = validate_secret_payload(data)
    if not secret_validation["ok"]:
        reasons.extend(secret_validation["reasons"])
        reasons.extend(secret_validation.get("findings", []))

    if data.get("real_network") is True:
        reasons.append("real_network_blocked_in_sandbox")

    if data.get("official_publish") is True:
        reasons.append("official_publish_blocked")

    if data.get("auto_publish") is True:
        reasons.append("auto_publish_blocked")

    if data.get("mass_messaging") is True:
        reasons.append("mass_messaging_blocked")

    if data.get("browser_automation") is True:
        reasons.append("browser_automation_blocked")

    if data.get("send_real_message") is True:
        reasons.append("real_message_send_blocked")

    if data.get("external_api_enabled") is True:
        reasons.append("external_api_enabled_not_allowed_in_sandbox_adapter")

    return {
        "ok": len(reasons) == 0,
        "mode": "sandbox_only",
        "network": "disabled",
        "reasons": reasons or ["sandbox_payload_allowed"],
    }
