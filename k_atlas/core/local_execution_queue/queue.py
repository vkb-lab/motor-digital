from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalExecutionQueue:
    def __init__(
        self,
        route_queue_path: str | Path = "live/local_action_router/action_route_queue.json",
        live_dir: str | Path = "live/local_execution_queue",
        reports_dir: str | Path = "reports/local_execution_queue",
        memory_dir: str | Path = "memory/local_execution_queue",
    ) -> None:
        self.route_queue_path = Path(route_queue_path)
        self.live_dir = Path(live_dir)
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.execution_queue_path = self.live_dir / "execution_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def enqueue_latest_ready_route(self) -> dict[str, Any]:
        routes = self.load_list(self.route_queue_path)
        queue = self.load_list(self.execution_queue_path)
        existing_route_ids = {item.get("route_id") for item in queue}

        ready = [
            item for item in routes
            if item.get("status") == "route_ready" and item.get("route_id") not in existing_route_ids
        ]

        if not ready:
            report = {
                "ok": False,
                "checkpoint": "86",
                "name": "Local Execution Queue",
                "generated_at": utc_now(),
                "status": "no_ready_route",
                "summary": {"queued_total": len(queue), "real_execution_enabled": False},
            }
            self.save_report(report)
            return report

        route = ready[-1]
        item = {
            "ok": True,
            "checkpoint": "86",
            "name": "Local Execution Queue Item",
            "execution_id": str(uuid4()),
            "route_id": route.get("route_id"),
            "action_type": route.get("action_type"),
            "status": "waiting_human_execution",
            "created_at": utc_now(),
            "suggested_command": route.get("suggested_command"),
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "real_execution_enabled": False,
            "external_side_effects": route.get("external_side_effects", "none"),
        }

        queue.append(item)
        self.save_list(self.execution_queue_path, queue)

        report = {
            "ok": True,
            "checkpoint": "86",
            "name": "Local Execution Queue",
            "generated_at": utc_now(),
            "status": "execution_item_queued",
            "queued_item": item,
            "summary": {
                "queued_total": len(queue),
                "waiting_human_execution": len([row for row in queue if row.get("status") == "waiting_human_execution"]),
                "real_execution_enabled": False,
                "automatic_execution_allowed": False,
            },
        }
        self.save_report(report)
        self.event("local_execution_queue.item_queued", {"execution_id": item["execution_id"]})
        return report

    def summary(self) -> dict[str, Any]:
        queue = self.load_list(self.execution_queue_path)
        return {
            "ok": True,
            "checkpoint": "86",
            "name": "Local Execution Queue",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "queued_total": len(queue),
                "waiting_human_execution": len([item for item in queue if item.get("status") == "waiting_human_execution"]),
                "real_execution_enabled": False,
                "automatic_execution_allowed": False,
            },
            "latest_item": queue[-1] if queue else None,
        }

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.reports_dir / "latest_local_execution_queue.json"
        md_path = self.reports_dir / "latest_local_execution_queue.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}
        return "\n".join([
            "# K-Atlas Local Execution Queue",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Queued total: {summary.get('queued_total')}",
            f"Waiting human execution: {summary.get('waiting_human_execution')}",
            f"Real execution enabled: {summary.get('real_execution_enabled')}",
        ])
