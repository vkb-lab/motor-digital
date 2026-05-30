from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalApiApprovalBridge:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/local_api_approval_bridge",
        memory_dir: str | Path = "memory/local_api_approval_bridge",
        reports_dir: str | Path = "reports/local_api_approval_bridge",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.queue_path = self.live_dir / "api_approval_queue.json"
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
        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def create_request(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        data = dict(payload or {})
        item = {
            "approval_request_id": str(uuid4()),
            "created_at": utc_now(),
            "status": "waiting_human_approval",
            "source": data.get("source", "local_api"),
            "intent": data.get("intent", "unspecified"),
            "payload": data,
            "automatic_execution_allowed": False,
            "real_execution_enabled": False,
            "external_side_effects": "queue_only",
        }

        queue = self.load_queue()
        queue.append(item)
        self.save_queue(queue)
        self.event("local_api_approval_bridge.request_created", {"approval_request_id": item["approval_request_id"]})
        self.save_report()
        return item

    def summary(self) -> dict[str, Any]:
        queue = self.load_queue()
        return {
            "ok": True,
            "checkpoint": "91",
            "name": "Local API Approval Bridge",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "approval_queue_total": len(queue),
                "waiting_human_approval": len([item for item in queue if item.get("status") == "waiting_human_approval"]),
                "automatic_execution_allowed": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
            },
            "queue": queue,
        }

    def save_report(self) -> dict[str, Any]:
        report = self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_local_api_approval_bridge.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_local_api_approval_bridge.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        return "\n".join([
            "# K-Atlas Local API Approval Bridge",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Approval queue total: {summary.get('approval_queue_total')}",
            f"- Waiting human approval: {summary.get('waiting_human_approval')}",
            f"- Real execution enabled: {summary.get('real_execution_enabled')}",
        ])
