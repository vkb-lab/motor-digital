from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from k_atlas.core.control_plane.event_bus import EventBus
from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue

from .policy import AutopilotPolicy


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupervisorAutopilot:
    def __init__(
        self,
        supervisor_queue: SupervisorQueue | None = None,
        event_bus: EventBus | None = None,
        policy: AutopilotPolicy | None = None,
        run_log_path: str | Path = "memory/supervisor_autopilot/autopilot_runs.json",
    ) -> None:
        self.supervisor_queue = supervisor_queue or SupervisorQueue()
        self.event_bus = event_bus or EventBus()
        self.policy = policy or AutopilotPolicy()
        self.run_log_path = Path(run_log_path)

    def load_runs(self) -> list[dict[str, Any]]:
        if not self.run_log_path.exists():
            return []

        data = json.loads(self.run_log_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return data

    def save_run(self, run: dict[str, Any]) -> None:
        self.run_log_path.parent.mkdir(parents=True, exist_ok=True)
        rows = self.load_runs()
        rows.append(run)
        self.run_log_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def run_once(self, reviewer: str = "k_supervisor_autopilot") -> dict[str, Any]:
        run_id = str(uuid4())
        approvals = self.supervisor_queue.load()

        approved: list[dict[str, Any]] = []
        blocked: list[dict[str, Any]] = []
        ignored: list[dict[str, Any]] = []

        self.event_bus.emit(
            event_type="autopilot.started",
            source="supervisor_autopilot",
            payload={"run_id": run_id},
        )

        for item in approvals:
            if item.get("status") != "pending_approval":
                ignored.append({
                    "approval_id": item.get("approval_id"),
                    "reason": "not_pending",
                })
                continue

            decision = self.policy.evaluate(item)

            if decision.ok:
                approved_item = self.supervisor_queue.approve(
                    approval_id=item["approval_id"],
                    reviewer=reviewer,
                )
                approved_item["autopilot_decision"] = decision.to_dict()
                approved.append(approved_item)

                self.event_bus.emit(
                    event_type="autopilot.approval.granted",
                    source="supervisor_autopilot",
                    payload={
                        "run_id": run_id,
                        "approval_id": item["approval_id"],
                        "decision": decision.to_dict(),
                    },
                )
            else:
                blocked_item = {
                    "approval_id": item.get("approval_id"),
                    "task": item.get("task", {}),
                    "decision": decision.to_dict(),
                }
                blocked.append(blocked_item)

                self.event_bus.emit(
                    event_type="autopilot.approval.blocked",
                    source="supervisor_autopilot",
                    payload={
                        "run_id": run_id,
                        "approval_id": item.get("approval_id"),
                        "decision": decision.to_dict(),
                    },
                    severity="warning",
                )

        run = {
            "run_id": run_id,
            "created_at": utc_now_iso(),
            "status": "completed",
            "approved_count": len(approved),
            "blocked_count": len(blocked),
            "ignored_count": len(ignored),
            "approved": approved,
            "blocked": blocked,
            "ignored": ignored,
        }

        self.save_run(run)

        self.event_bus.emit(
            event_type="autopilot.finished",
            source="supervisor_autopilot",
            payload={
                "run_id": run_id,
                "approved_count": len(approved),
                "blocked_count": len(blocked),
                "ignored_count": len(ignored),
            },
        )

        return run
