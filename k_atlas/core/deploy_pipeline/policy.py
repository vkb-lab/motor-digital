from __future__ import annotations

from typing import Any, Mapping

from k_atlas.core.credential_vault.policy import validate_secret_payload


def validate_deploy_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})
    reasons: list[str] = []

    secret_validation = validate_secret_payload(data)
    if not secret_validation["ok"]:
        reasons.append("plaintext_secret_blocked")

    if data.get("auto_deploy") is True:
        reasons.append("auto_deploy_blocked")

    if data.get("force_push") is True:
        reasons.append("force_push_blocked")

    if data.get("production_mutation") is True:
        reasons.append("production_mutation_requires_human_review")

    if data.get("official_publish") is True:
        reasons.append("official_publish_blocked")

    return {
        "ok": len(reasons) == 0,
        "status": "deploy_payload_valid" if not reasons else "deploy_payload_blocked",
        "reasons": reasons or ["deploy_allowed_for_assisted_pipeline"],
    }
