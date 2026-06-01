from dataclasses import dataclass, asdict
from typing import Any, Dict
from datetime import datetime


@dataclass
class ApprovalRequest:
    id: str
    action: str
    payload: Dict[str, Any]
    status: str = "PENDING_APPROVAL"
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_approval(action: str, payload: Dict[str, Any] | None = None, requested_by: str = "system") -> Dict[str, Any]:
    payload = payload or {}
    payload["requested_by"] = requested_by
    return ApprovalRequest(
        id=f"approval_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        action=action,
        payload=payload,
    ).to_dict()


class ApprovalFlow:
    def create(self, action: str, payload: Dict[str, Any] | None = None, requested_by: str = "system") -> Dict[str, Any]:
        return create_approval(action, payload, requested_by)
