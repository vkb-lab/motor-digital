from __future__ import annotations

from typing import Any, Mapping


SENSITIVE_KEYS = ("token", "secret", "password", "api_key", "access_key", "credential")


def find_sensitive_plaintext(data: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            lowered = key_text.lower()

            if any(part in lowered for part in SENSITIVE_KEYS):
                if value not in (None, "", []):
                    if not (isinstance(value, str) and value.startswith("vault://")):
                        findings.append(path)

            findings.extend(find_sensitive_plaintext(value, path))

    elif isinstance(data, list):
        for index, item in enumerate(data):
            findings.extend(find_sensitive_plaintext(item, f"{prefix}[{index}]"))

    return sorted(set(findings))


def validate_creative_media_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []

    sensitive = find_sensitive_plaintext(payload)
    if sensitive:
        reasons.append("plaintext_secret_blocked:" + ",".join(sensitive))

    if bool(payload.get("auto_publish")):
        reasons.append("auto_publish_blocked")

    if bool(payload.get("official_publish")):
        reasons.append("official_publish_blocked_until_level_4")

    if bool(payload.get("external_api_enabled")) and not payload.get("credential_vault_ref"):
        reasons.append("external_api_requires_credential_vault")

    if bool(payload.get("browser_automation")):
        reasons.append("browser_automation_blocked")

    if bool(payload.get("mass_messaging")):
        reasons.append("mass_messaging_blocked")

    return {
        "ok": len(reasons) == 0,
        "mode": "planning_only",
        "reasons": reasons or ["creative_payload_allowed_for_planning"],
    }