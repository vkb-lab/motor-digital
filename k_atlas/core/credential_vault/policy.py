from __future__ import annotations

from typing import Any, Mapping


SENSITIVE_KEYS = (
    "token",
    "secret",
    "password",
    "api_key",
    "access_key",
    "credential",
    "bearer",
)


def mask_secret(value: str | None) -> str:
    if not value:
        return ""

    text = str(value)

    if len(text) <= 8:
        return "*" * len(text)

    return text[:4] + ("*" * max(4, len(text) - 8)) + text[-4:]


def find_plaintext_secrets(data: Any, prefix: str = "") -> list[str]:
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

            findings.extend(find_plaintext_secrets(value, path))

    elif isinstance(data, list):
        for index, item in enumerate(data):
            findings.extend(find_plaintext_secrets(item, f"{prefix}[{index}]"))

    return sorted(set(findings))


def validate_secret_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    findings = find_plaintext_secrets(payload)

    if findings:
        return {
            "ok": False,
            "status": "blocked_plaintext_secret",
            "findings": findings,
            "reasons": ["plaintext_secret_not_allowed"],
        }

    return {
        "ok": True,
        "status": "secret_policy_passed",
        "findings": [],
        "reasons": ["no_plaintext_secret_detected"],
    }
