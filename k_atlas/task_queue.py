from dataclasses import dataclass, asdict
from typing import Any, Dict, List
from datetime import datetime


@dataclass
class Task:
    id: str
    agent: str
    action: str
    payload: Dict[str, Any]
    status: str = "QUEUED"
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TaskQueue:
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []

    def add_task(self, agent: str, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        task = Task(
            id=f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            agent=agent,
            action=action,
            payload=payload or {},
        ).to_dict()
        self.tasks.append(task)
        return task

    def list_tasks(self) -> List[Dict[str, Any]]:
        return list(self.tasks)
