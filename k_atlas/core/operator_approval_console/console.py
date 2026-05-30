from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_approval_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperatorApprovalConsole:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/operator_approval_console",
        memory_dir: str | Path = "memory/operator_approval_console",
        reports_dir: str | Path = "reports/operator_approval_console",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.queue_path = self.live_dir / "approval_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def load_queue(self) -> list[dict[str, Any]]:
        if not self.queue_path.exists():
            return []
        try:
            data = json.loads(self.queue_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_queue(self, rows: list[dict[str, Any]]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"timestamp": utc_now(), "event_type": event_type, "payload": payload}, ensure_ascii=False, sort_keys=True) + "\n")

    def create_request(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        data = dict(payload or {})
        validation = validate_approval_request(data)
        request_id = str(uuid4())

        item = {
            "approval_request_id": request_id,
            "created_at": utc_now(),
            "status": "waiting_operator_decision" if validation["ok"] else "blocked_by_policy",
            "request": data,
            "validation": validation,
            "decision": None,
            "execution_allowed": False,
            "automatic_execution_allowed": False,
            "external_side_effects": "none",
        }

        queue = self.load_queue()
        queue.append(item)
        self.save_queue(queue)
        self.save_report()
        self.event("operator_approval_console.request_created", {"approval_request_id": request_id, "status": item["status"]})
        return item

    def decide(self, approval_request_id: str, decision: str, operator: str = "operator", notes: str = "") -> dict[str, Any]:
        if decision not in {"approve", "reject"}:
            raise ValueError("decision must be approve or reject")

        queue = self.load_queue()
        for item in queue:
            if item.get("approval_request_id") == approval_request_id:
                if item.get("status") != "waiting_operator_decision":
                    item["decision"] = {"decision": "not_allowed", "operator": operator, "notes": "request_not_waiting"}
                else:
                    item["status"] = "approved_by_operator" if decision == "approve" else "rejected_by_operator"
                    item["decision"] = {
                        "decision": decision,
                        "operator": operator,
                        "notes": notes,
                        "decided_at": utc_now(),
                    }
                    item["execution_allowed"] = decision == "approve"
                self.save_queue(queue)
                self.save_report()
                self.event("operator_approval_console.request_decided", {"approval_request_id": approval_request_id, "decision": decision})
                return item

        raise KeyError(f"approval_request_id not found: {approval_request_id}")

    def summary(self) -> dict[str, Any]:
        queue = self.load_queue()
        return {
            "ok": True,
            "checkpoint": "80",
            "name": "Operator Approval Console",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "approval_queue_total": len(queue),
                "waiting_operator_decision": len([x for x in queue if x.get("status") == "waiting_operator_decision"]),
                "approved_by_operator": len([x for x in queue if x.get("status") == "approved_by_operator"]),
                "rejected_by_operator": len([x for x in queue if x.get("status") == "rejected_by_operator"]),
                "blocked_by_policy": len([x for x in queue if x.get("status") == "blocked_by_policy"]),
                "automatic_execution_allowed": False,
            },
            "queue": queue,
        }

    def save_report(self) -> dict[str, Any]:
        report = self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_operator_approval_console.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        (self.reports_dir / "latest_operator_approval_console.md").write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        return "\n".join([
            "# K-Atlas Operator Approval Console",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Queue total: {summary.get('approval_queue_total')}",
            f"- Waiting: {summary.get('waiting_operator_decision')}",
            f"- Approved: {summary.get('approved_by_operator')}",
            f"- Rejected: {summary.get('rejected_by_operator')}",
            f"- Auto execution allowed: {summary.get('automatic_execution_allowed')}",
        ])
