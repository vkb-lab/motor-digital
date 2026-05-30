from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpdateIntakeQueue:
    def __init__(
        self,
        live_dir: str | Path = "live/update_intake_queue",
        memory_dir: str | Path = "memory/update_intake_queue",
        reports_dir: str | Path = "reports/update_intake_queue",
    ) -> None:
        self.live_dir = Path(live_dir)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.queue_path = self.live_dir / "update_queue.json"
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
        row = {"timestamp": utc_now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def enqueue(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = dict(payload or {})
        item = {
            "update_id": str(uuid4()),
            "created_at": utc_now(),
            "status": "queued_for_verification",
            "source": data.get("source", "local_download"),
            "installer_name": data.get("installer_name", "K_ATLAS_DEMO_UPDATE.ps1"),
            "human_approval_required": True,
            "automatic_public_access_allowed": False,
            "external_side_effects": "none",
            "metadata": data,
        }

        queue = self.load_queue()
        queue.append(item)
        self.save_queue(queue)
        self.event("update_intake_queue.enqueued", {"update_id": item["update_id"]})

        return item

    def build_report(self) -> dict[str, Any]:
        queue = self.load_queue()
        report = {
            "ok": True,
            "checkpoint": "113",
            "name": "Update Intake Queue",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "queued_updates": len(queue),
                "execution_enabled": False,
                "external_side_effects": "none",
            },
            "updates": queue,
        }
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_update_intake_queue.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return report
