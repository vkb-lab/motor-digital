from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any

from .policy import mask_secret


@dataclass(frozen=True)
class CredentialRef:
    provider: str
    key: str
    ref: str
    exists: bool
    masked_preview: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CredentialVault:
    PREFIX = "vault://env/"

    def build_ref(self, env_name: str) -> str:
        clean = env_name.strip().upper()
        return f"{self.PREFIX}{clean}"

    def parse_ref(self, ref: str) -> str:
        if not ref.startswith(self.PREFIX):
            raise ValueError("credential_ref_deve_usar_vault_env")

        key = ref.replace(self.PREFIX, "", 1).strip().upper()

        if not key:
            raise ValueError("credential_ref_sem_chave")

        return key

    def inspect_env(self, env_name: str) -> CredentialRef:
        key = env_name.strip().upper()
        value = os.environ.get(key)

        return CredentialRef(
            provider="env",
            key=key,
            ref=self.build_ref(key),
            exists=bool(value),
            masked_preview=mask_secret(value),
        )

    def inspect_ref(self, ref: str) -> CredentialRef:
        key = self.parse_ref(ref)
        return self.inspect_env(key)

    def require_ref(self, ref: str) -> dict[str, Any]:
        inspected = self.inspect_ref(ref)

        if not inspected.exists:
            return {
                "ok": False,
                "status": "missing_credential",
                "credential": inspected.to_dict(),
                "reasons": ["environment_variable_not_found"],
            }

        return {
            "ok": True,
            "status": "credential_available",
            "credential": inspected.to_dict(),
            "reasons": ["credential_found_but_not_exposed"],
        }

    def inspect_many(self, env_names: list[str]) -> list[dict[str, Any]]:
        return [self.inspect_env(name).to_dict() for name in env_names]
