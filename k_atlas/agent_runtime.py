from typing import Any, Dict
from k_atlas.permissions import check_permission


def run_agent(agent: str, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    decision = check_permission(agent, "EXECUTE")
    return {
        "agent": agent,
        "action": action,
        "payload": payload or {},
        "status": "EXECUTED" if decision.allowed else decision.status,
        "permission": decision.to_dict(),
    }


class AgentRuntime:
    def run(self, agent: str, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return run_agent(agent, action, payload)
