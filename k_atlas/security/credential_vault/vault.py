from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping


class VaultResolutionError(RuntimeError):
    pass


SENSITIVE_KEY_PARTS = ("token", "secret", "password", "api_key", "access_key", "credential")


def is_vault_ref(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("vault://")


def parse_vault_ref(vault_ref: str) -> tuple[str, str]:
    if not is_vault_ref(vault_ref):
        raise VaultResolutionError("Valor nao e vault ref.")

    raw = vault_ref.replace("vault://", "", 1)
    parts = raw.split("/", 1)

    if len(parts) != 2:
        raise VaultResolutionError("Formato esperado: vault://env/NOME_DA_VARIAVEL")

    provider, key = parts[0].strip(), parts[1].strip()

    if provider != "env":
        raise VaultResolutionError("Provider permitido agora: env")

    if not key:
        raise VaultResolutionError("Nome da variavel de ambiente vazio.")

    return provider, key


def resolve_secret(vault_ref: str) -> str:
    provider, key = parse_vault_ref(vault_ref)

    if provider != "env":
        raise VaultResolutionError("Provider nao suportado.")

    value = os.getenv(key)

    if value is None or not value.strip():
        raise VaultResolutionError(f"Variavel de ambiente ausente: {key}")

    return value


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def redact(value: Any) -> str:
    if value in (None, ""):
        return ""
    return "[REDACTED]"


def sanitize_mapping(data: Any) -> Any:
    if isinstance(data, Mapping):
        clean: dict[str, Any] = {}
        for key, value in data.items():
            key_text = str(key)
            lowered = key_text.lower()

            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                clean[key_text] = redact(value)
            else:
                clean[key_text] = sanitize_mapping(value)

        return clean

    if isinstance(data, list):
        return [sanitize_mapping(item) for item in data]

    if isinstance(data, tuple):
        return [sanitize_mapping(item) for item in data]

    return data


def find_plaintext_secrets(data: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_text = str(key)
            lowered = key_text.lower()
            path = f"{prefix}.{key_text}" if prefix else key_text

            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                if value not in (None, "", []):
                    if not is_vault_ref(value):
                        findings.append(path)

            findings.extend(find_plaintext_secrets(value, path))

    elif isinstance(data, list):
        for index, item in enumerate(data):
            findings.extend(find_plaintext_secrets(item, f"{prefix}[{index}]"))

    return sorted(set(findings))


@dataclass(frozen=True)
class VaultCheckResult:
    ok: bool
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "reasons": list(self.reasons),
        }


def validate_no_plaintext_secrets(data: Mapping[str, Any]) -> VaultCheckResult:
    findings = find_plaintext_secrets(data)

    if findings:
        return VaultCheckResult(
            ok=False,
            reasons=["plaintext_secret_blocked:" + ",".join(findings)],
        )

    return VaultCheckResult(ok=True, reasons=["no_plaintext_secrets_found"])