"""Permission helpers for K-OS orchestration.

This module is intentionally dependency-free so Phase 2 orchestration can
import it on clean Windows environments and in CI.  The default policy is
conservative: known operational permissions are allowed and unknown actions
are denied unless an explicit caller-provided policy enables them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping


READ = "read"
WRITE = "write"
EXECUTE = "execute"
REPORT = "report"
ORCHESTRATE = "orchestrate"
HEALTHCHECK = "healthcheck"
VALIDATE = "validate"

DEFAULT_ALLOWED_PERMISSIONS = frozenset(
    {
        READ,
        WRITE,
        EXECUTE,
        REPORT,
        ORCHESTRATE,
        HEALTHCHECK,
        VALIDATE,
    }
)


@dataclass(frozen=True)
class PermissionDecision:
    """Structured result returned by permission checks."""

    allowed: bool
    permission: str
    reason: str = ""

    def __bool__(self) -> bool:
        return self.allowed


@dataclass
class PermissionPolicy:
    """Small allow-list based permission policy."""

    allowed_permissions: set[str] = field(
        default_factory=lambda: set(DEFAULT_ALLOWED_PERMISSIONS)
    )
    denied_permissions: set[str] = field(default_factory=set)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Iterable[str]] | None) -> "PermissionPolicy":
        if not data:
            return cls()
        allowed = set(data.get("allowed_permissions", DEFAULT_ALLOWED_PERMISSIONS))
        denied = set(data.get("denied_permissions", ()))
        return cls(allowed_permissions=allowed, denied_permissions=denied)

    def is_allowed(self, permission: str) -> bool:
        normalized = normalize_permission(permission)
        return normalized in self.allowed_permissions and normalized not in self.denied_permissions

    def check(self, permission: str) -> PermissionDecision:
        normalized = normalize_permission(permission)
        if normalized in self.denied_permissions:
            return PermissionDecision(False, normalized, "permission explicitly denied")
        if normalized in self.allowed_permissions:
            return PermissionDecision(True, normalized, "permission allowed")
        return PermissionDecision(False, normalized, "permission not in allow list")

    def grant(self, permission: str) -> None:
        normalized = normalize_permission(permission)
        self.denied_permissions.discard(normalized)
        self.allowed_permissions.add(normalized)

    def deny(self, permission: str) -> None:
        normalized = normalize_permission(permission)
        self.allowed_permissions.discard(normalized)
        self.denied_permissions.add(normalized)

    def as_dict(self) -> MutableMapping[str, list[str]]:
        return {
            "allowed_permissions": sorted(self.allowed_permissions),
            "denied_permissions": sorted(self.denied_permissions),
        }


class PermissionManager:
    """Compatibility facade used by orchestration code."""

    def __init__(self, policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None) -> None:
        self.policy = policy if isinstance(policy, PermissionPolicy) else PermissionPolicy.from_mapping(policy)

    def check(self, permission: str) -> PermissionDecision:
        return self.policy.check(permission)

    def is_allowed(self, permission: str) -> bool:
        return self.policy.is_allowed(permission)

    def require(self, permission: str) -> None:
        require_permission(permission, self.policy)

    def grant(self, permission: str) -> None:
        self.policy.grant(permission)

    def deny(self, permission: str) -> None:
        self.policy.deny(permission)


PermissionGate = PermissionManager


def normalize_permission(permission: str) -> str:
    if permission is None:
        return ""
    return str(permission).strip().lower().replace("-", "_")


def is_allowed(permission: str, policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None) -> bool:
    return check_permission(permission, policy).allowed


def check_permission(
    permission: str,
    policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None,
) -> PermissionDecision:
    active_policy = policy if isinstance(policy, PermissionPolicy) else PermissionPolicy.from_mapping(policy)
    return active_policy.check(permission)


def require_permission(
    permission: str,
    policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None,
) -> None:
    decision = check_permission(permission, policy)
    if not decision.allowed:
        raise PermissionError(f"{decision.permission}: {decision.reason}")


def has_permission(
    permission: str,
    policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None,
) -> bool:
    return is_allowed(permission, policy)


def validate_permission(
    permission: str,
    policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None,
) -> PermissionDecision:
    return check_permission(permission, policy)


def can_read(policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None) -> bool:
    return is_allowed(READ, policy)


def can_write(policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None) -> bool:
    return is_allowed(WRITE, policy)


def can_execute(policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None) -> bool:
    return is_allowed(EXECUTE, policy)


def can_orchestrate(policy: PermissionPolicy | Mapping[str, Iterable[str]] | None = None) -> bool:
    return is_allowed(ORCHESTRATE, policy)


__all__ = [
    "DEFAULT_ALLOWED_PERMISSIONS",
    "EXECUTE",
    "HEALTHCHECK",
    "ORCHESTRATE",
    "PermissionDecision",
    "PermissionGate",
    "PermissionManager",
    "PermissionPolicy",
    "READ",
    "REPORT",
    "VALIDATE",
    "WRITE",
    "can_execute",
    "can_orchestrate",
    "can_read",
    "can_write",
    "check_permission",
    "has_permission",
    "is_allowed",
    "normalize_permission",
    "require_permission",
    "validate_permission",
]
