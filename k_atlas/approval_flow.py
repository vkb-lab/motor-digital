from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict
from datetime import datetime


class ApprovalStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class ApprovalRequest:
    id: str
    action: str
    payload: Dict[str, Any]
    status: str = ApprovalStatus.PENDING_APPROVAL.value
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)


def create_approval(action: str, payload: Dict[str, Any], requested_by: str = "system") -> Dict[str, Any]:
    return ApprovalRequest(
        id=f"approval_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        action=action,
        payload={**payload, "requested_by": requested_by},
    ).to_dict()


class ApprovalFlow:
    def create(self, action: str, payload: Dict[str, Any], requested_by: str = "system") -> Dict[str, Any]:
        return create_approval(action, payload, requested_by)
