# -*- coding: utf-8 -*-
"""
K-Atlas OS - Permission Manager

Camada inicial de permissões.
Simples, explícita e preparada para expansão futura com usuários, tenants e cloud.
"""

from __future__ import annotations

import fnmatch
import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set


class KAtlasPermissionError(PermissionError):
    """Erro de permissão operacional do K-Atlas OS."""


@dataclass(frozen=True)
class PermissionDecision:
    agent_id: str
    permission: str
    allowed: bool
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "permission": self.permission,
            "allowed": self.allowed,
            "reason": self.reason,
        }


class PermissionManager:
    """
    Gerencia permissões por agente e por papel.

    Convenção de permissões:
    - kernel.start
    - kernel.stop
    - registry.read
    - registry.write
    - router.dispatch
    - agent.execute
    - memory.read
    - memory.write
    - campaign.create
    - api.call
    - worker.run

    Wildcards são suportados:
    - *
    - kernel.*
    - memory.*
    """

    DEFAULT_ROLES: Dict[str, Set[str]] = {
        "admin": {"*"},
        "system": {
            "kernel.*",
            "registry.*",
            "router.*",
            "events.*",
            "agent.*",
            "memory.*",
            "campaign.*",
            "api.*",
            "worker.*",
            "cloud.*",
        },
        "operator": {
            "kernel.status",
            "registry.read",
            "router.dispatch",
            "events.read",
            "agent.read",
            "agent.execute",
            "memory.read",
            "campaign.*",
        },
        "agent": {
            "events.publish",
            "agent.read",
            "agent.execute",
            "memory.read",
            "memory.write",
        },
        "read_only": {
            "kernel.status",
            "registry.read",
            "events.read",
            "agent.read",
        },
    }

    def __init__(self) -> None:
        self._roles: Dict[str, Set[str]] = {
            role: set(permissions)
            for role, permissions in self.DEFAULT_ROLES.items()
        }
        self._agent_roles: Dict[str, Set[str]] = {
            "kernel": {"system"},
            "system": {"system"},
        }
        self._agent_permissions: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()

    def register_role(self, role: str, permissions: Iterable[str], replace: bool = False) -> None:
        """Cria ou atualiza um papel."""
        clean_role = self._normalize(role)
        with self._lock:
            if replace or clean_role not in self._roles:
                self._roles[clean_role] = set(permissions)
            else:
                self._roles[clean_role].update(permissions)

    def assign_role(self, agent_id: str, role: str) -> None:
        """Atribui papel a um agente ou ator."""
        clean_agent_id = self._normalize(agent_id)
        clean_role = self._normalize(role)

        with self._lock:
            if clean_role not in self._roles:
                raise KAtlasPermissionError(f"Papel inexistente: {clean_role}")
            self._agent_roles.setdefault(clean_agent_id, set()).add(clean_role)

    def revoke_role(self, agent_id: str, role: str) -> None:
        """Remove papel de um agente ou ator."""
        clean_agent_id = self._normalize(agent_id)
        clean_role = self._normalize(role)

        with self._lock:
            self._agent_roles.setdefault(clean_agent_id, set()).discard(clean_role)

    def grant(self, agent_id: str, permission: str) -> None:
        """Concede permissão direta a um agente."""
        clean_agent_id = self._normalize(agent_id)
        with self._lock:
            self._agent_permissions.setdefault(clean_agent_id, set()).add(permission)

    def grant_many(self, agent_id: str, permissions: Iterable[str]) -> None:
        """Concede várias permissões diretas."""
        for permission in permissions:
            self.grant(agent_id, permission)

    def revoke(self, agent_id: str, permission: str) -> None:
        """Revoga permissão direta."""
        clean_agent_id = self._normalize(agent_id)
        with self._lock:
            self._agent_permissions.setdefault(clean_agent_id, set()).discard(permission)

    def can(self, agent_id: str, permission: str) -> PermissionDecision:
        """Verifica se um agente possui permissão."""
        clean_agent_id = self._normalize(agent_id)

        with self._lock:
            direct_permissions = set(self._agent_permissions.get(clean_agent_id, set()))
            role_names = set(self._agent_roles.get(clean_agent_id, set()))

            role_permissions: Set[str] = set()
            for role_name in role_names:
                role_permissions.update(self._roles.get(role_name, set()))

        all_permissions = direct_permissions | role_permissions

        for candidate in all_permissions:
            if self._match(candidate, permission):
                return PermissionDecision(
                    agent_id=clean_agent_id,
                    permission=permission,
                    allowed=True,
                    reason=f"Permitido por '{candidate}'.",
                )

        return PermissionDecision(
            agent_id=clean_agent_id,
            permission=permission,
            allowed=False,
            reason="Permissão não encontrada.",
        )

    def require(self, agent_id: str, permission: str) -> None:
        """Exige permissão ou gera erro."""
        decision = self.can(agent_id, permission)
        if not decision.allowed:
            raise KAtlasPermissionError(
                f"Acesso negado para '{decision.agent_id}' em '{decision.permission}'. "
                f"Motivo: {decision.reason}"
            )

    def permissions_for(self, agent_id: str) -> List[str]:
        """Lista permissões finais de um agente."""
        clean_agent_id = self._normalize(agent_id)

        with self._lock:
            direct_permissions = set(self._agent_permissions.get(clean_agent_id, set()))
            role_names = set(self._agent_roles.get(clean_agent_id, set()))

            role_permissions: Set[str] = set()
            for role_name in role_names:
                role_permissions.update(self._roles.get(role_name, set()))

        return sorted(direct_permissions | role_permissions)

    def roles_for(self, agent_id: str) -> List[str]:
        """Lista papéis de um agente."""
        clean_agent_id = self._normalize(agent_id)
        with self._lock:
            return sorted(self._agent_roles.get(clean_agent_id, set()))

    def to_dict(self) -> Dict[str, object]:
        """Exporta estado serializável."""
        with self._lock:
            return {
                "roles": {key: sorted(value) for key, value in self._roles.items()},
                "agent_roles": {key: sorted(value) for key, value in self._agent_roles.items()},
                "agent_permissions": {
                    key: sorted(value) for key, value in self._agent_permissions.items()
                },
            }

    def save_json(self, path: str | Path) -> None:
        """Salva permissões em JSON."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2, sort_keys=True)

    def load_json(self, path: str | Path) -> None:
        """Carrega permissões de JSON."""
        file_path = Path(path)
        if not file_path.exists():
            return

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        with self._lock:
            self._roles = {
                key: set(value)
                for key, value in data.get("roles", {}).items()
            }
            self._agent_roles = {
                key: set(value)
                for key, value in data.get("agent_roles", {}).items()
            }
            self._agent_permissions = {
                key: set(value)
                for key, value in data.get("agent_permissions", {}).items()
            }

    @staticmethod
    def _normalize(value: str) -> str:
        clean = str(value).strip()
        if not clean:
            raise ValueError("Identificador vazio não é permitido.")
        return clean

    @staticmethod
    def _match(rule: str, permission: str) -> bool:
        return rule == "*" or fnmatch.fnmatchcase(permission, rule)
