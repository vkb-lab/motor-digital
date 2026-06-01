from typing import Any, Dict
from k_atlas.permissions import check_permission
from k_atlas.task_queue import TaskQueue


class Orchestrator:
    def __init__(self):
        self.queue = TaskQueue()

    def delegate_task(self, agent: str, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        decision = check_permission(agent, "EXECUTE")
        task = self.queue.add_task(agent, action, payload or {})
        task["permission"] = decision.to_dict()
        task["status"] = "QUEUED" if decision.allowed else decision.status
        return task

    def create_campaign_task(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.delegate_task("CampaignAgent", "create_campaign", payload or {})
