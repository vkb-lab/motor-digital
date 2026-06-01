from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class PermissionDecision:
    allowed: bool
    status: str
    reason: str
    agent: str
    permission: str
    approval_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEFAULT_AGENT_PERMISSIONS: Dict[str, List[str]] = {
    "MemoryAgent": ["READ", "WRITE", "EXECUTE"],
    "CampaignAgent": ["READ", "WRITE", "EXECUTE"],
    "ReportAgent": ["READ", "WRITE", "EXECUTE"],
    "SystemAgent": ["READ", "EXECUTE"],
    "AuditorAgent": ["READ", "EXECUTE"],
}


def normalize_permission(permission: str) -> str:
    return str(permission or "READ").upper().strip()


def get_agent_permissions(agent: str) -> List[str]:
    return DEFAULT_AGENT_PERMISSIONS.get(agent, ["READ"])


def check_permission(agent: str, permission: str, sensitive: bool = False, external: bool = False) -> PermissionDecision:
    permission = normalize_permission(permission)

    if sensitive or external or permission in {"SENSITIVE", "EXTERNAL"}:
        return PermissionDecision(
            allowed=False,
            status="PENDING_APPROVAL",
            reason="Acao sensivel requer aprovacao manual.",
            agent=agent,
            permission=permission,
            approval_required=True,
        )

    allowed = permission in get_agent_permissions(agent)
    return PermissionDecision(
        allowed=allowed,
        status="ALLOWED" if allowed else "DENIED",
        reason="Permissao concedida." if allowed else "Permissao negada.",
        agent=agent,
        permission=permission,
        approval_required=False,
    )


def require_permission(agent: str, permission: str, sensitive: bool = False, external: bool = False) -> PermissionDecision:
    return check_permission(agent, permission, sensitive=sensitive, external=external)


class PermissionManager:
    def check_permission(self, agent: str, permission: str, sensitive: bool = False, external: bool = False) -> PermissionDecision:
        return check_permission(agent, permission, sensitive=sensitive, external=external)

    def require_permission(self, agent: str, permission: str, sensitive: bool = False, external: bool = False) -> PermissionDecision:
        return require_permission(agent, permission, sensitive=sensitive, external=external)
