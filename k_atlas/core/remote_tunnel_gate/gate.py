from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_tunnel_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RemoteTunnelGate:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/remote_tunnel_gate",
        memory_dir: str | Path = "memory/remote_tunnel_gate",
        reports_dir: str | Path = "reports/remote_tunnel_gate",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.queue_path = self.live_dir / "tunnel_gate_queue.json"
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
        data = dict(payload or {"provider": "manual"})
        validation = validate_tunnel_request(data)
        request_id = str(uuid4())

        item = {
            "tunnel_request_id": request_id,
            "created_at": utc_now(),
            "status": "waiting_human_remote_review" if validation["ok"] else "blocked_by_policy",
            "provider": data.get("provider", "manual"),
            "request": data,
            "validation": validation,
            "tunnel_started": False,
            "public_url_created": False,
            "token_stored": False,
            "execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "gate nao inicia tunel",
                "gate nao armazena token",
                "gate nao expoe porta publica",
                "gate exige aprovacao humana futura",
            ],
        }

        queue = self.load_queue()
        queue.append(item)
        self.save_queue(queue)
        self.save_report()
        self.event("remote_tunnel_gate.request_created", {"tunnel_request_id": request_id, "status": item["status"]})
        return item

    def summary(self) -> dict[str, Any]:
        queue = self.load_queue()
        return {
            "ok": True,
            "checkpoint": "82",
            "name": "Remote Tunnel Gate",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "tunnel_queue_total": len(queue),
                "waiting_human_remote_review": len([x for x in queue if x.get("status") == "waiting_human_remote_review"]),
                "blocked_by_policy": len([x for x in queue if x.get("status") == "blocked_by_policy"]),
                "tunnel_started": False,
                "public_url_created": False,
                "token_stored": False,
            },
            "queue": queue,
        }

    def save_report(self) -> dict[str, Any]:
        report = self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_remote_tunnel_gate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        (self.reports_dir / "latest_remote_tunnel_gate.md").write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        return "\n".join([
            "# K-Atlas Remote Tunnel Gate",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Queue total: {summary.get('tunnel_queue_total')}",
            f"- Waiting review: {summary.get('waiting_human_remote_review')}",
            f"- Tunnel started: {summary.get('tunnel_started')}",
            f"- Public URL created: {summary.get('public_url_created')}",
            f"- Token stored: {summary.get('token_stored')}",
        ])
