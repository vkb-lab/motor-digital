from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from uuid import uuid4

from .agent_registry import AgentRegistry, build_default_agent_registry
from .autonomy_policy import AutonomyPolicy, ControlDecision
from .event_bus import EventBus
from .supervisor_queue import SupervisorQueue


@dataclass(frozen=True)
class RouteResult:
    ok: bool
    status: str
    task: dict[str, Any]
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "task": self.task,
            "reasons": list(self.reasons),
        }


class TaskRouter:
    def __init__(
        self,
        registry: AgentRegistry | None = None,
        policy: AutonomyPolicy | None = None,
        event_bus: EventBus | None = None,
        supervisor_queue: SupervisorQueue | None = None,
    ) -> None:
        self.registry = registry or build_default_agent_registry()
        self.policy = policy or AutonomyPolicy()
        self.event_bus = event_bus or EventBus()
        self.supervisor_queue = supervisor_queue or SupervisorQueue()

    def route(
        self,
        objective: str,
        agent_id: str,
        action: str,
        payload: Mapping[str, Any] | None = None,
        requested_by: str = "human_operator",
    ) -> RouteResult:
        agent = self.registry.get(agent_id)
        request_payload = dict(payload or {})

        task = {
            "task_id": str(uuid4()),
            "objective": objective,
            "agent_id": agent_id,
            "agent_name": agent.name,
            "action": action,
            "payload": request_payload,
            "requested_by": requested_by,
        }

        self.event_bus.emit(
            event_type="task.created",
            source="control_plane.task_router",
            payload=task,
        )

        policy_result = self.policy.evaluate(agent, action, request_payload)

        if policy_result.decision == ControlDecision.DENY:
            self.event_bus.emit(
                event_type="task.denied",
                source="control_plane.task_router",
                payload={
                    "task": task,
                    "policy": policy_result.to_dict(),
                },
                severity="warning",
            )
            return RouteResult(False, "denied", task, policy_result.reasons)

        if policy_result.decision == ControlDecision.REQUIRE_APPROVAL:
            approval = self.supervisor_queue.enqueue(
                task=task,
                reasons=policy_result.reasons,
                requested_by=requested_by,
            )
            self.event_bus.emit(
                event_type="approval.required",
                source="control_plane.task_router",
                payload={
                    "task": task,
                    "approval": approval,
                },
            )
            return RouteResult(True, "pending_approval", task, policy_result.reasons)

        self.event_bus.emit(
            event_type="task.allowed",
            source="control_plane.task_router",
            payload={
                "task": task,
                "policy": policy_result.to_dict(),
            },
        )
        return RouteResult(True, "allowed", task, policy_result.reasons)