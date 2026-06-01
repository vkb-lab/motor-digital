from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List
from datetime import datetime


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


@dataclass
class Task:
    id: str
    agent: str
    action: str
    payload: Dict[str, Any]
    status: str = TaskStatus.QUEUED.value
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)


class TaskQueue:
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []

    def add_task(self, agent: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        task = Task(
            id=f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            agent=agent,
            action=action,
            payload=payload,
        ).to_dict()
        self.tasks.append(task)
        return task

    def list_tasks(self) -> List[Dict[str, Any]]:
        return list(self.tasks)
