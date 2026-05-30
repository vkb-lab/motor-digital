from __future__ import annotations

from typing import Any, Mapping

from k_atlas.core.credential_vault.policy import validate_secret_payload


def validate_autonomy_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    secret_validation = validate_secret_payload(data)
    if not secret_validation["ok"]:
        reasons.append("plaintext_secret_blocked")

    if data.get("official_publish") is True:
        reasons.append("official_publish_blocked_until_level_4")

    if data.get("auto_publish") is True:
        reasons.append("auto_publish_blocked")

    if data.get("auto_deploy") is True:
        reasons.append("auto_deploy_blocked")

    if data.get("mass_messaging") is True:
        reasons.append("mass_messaging_blocked")

    if data.get("browser_automation") is True:
        reasons.append("browser_automation_blocked_for_official_ops")

    if data.get("external_api_enabled") is True and not data.get("credential_vault_ref"):
        reasons.append("external_api_requires_credential_vault")

    return {
        "ok": len(reasons) == 0,
        "status": "autonomy_payload_allowed" if not reasons else "autonomy_payload_blocked",
        "reasons": reasons or ["assisted_autonomy_allowed"],
    }
