from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SocialAuditLiveStatus:
    def __init__(
        self,
        status_path: str | Path = "memory/social_audit/live_status.json",
        events_path: str | Path = "memory/social_audit/live_events.jsonl",
    ) -> None:
        self.status_path = Path(status_path)
        self.events_path = Path(events_path)

    def update(
        self,
        run_id: str,
        status: str,
        step: str,
        message: str,
        data: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        self.events_path.parent.mkdir(parents=True, exist_ok=True)

        event = {
            "timestamp": utc_now_iso(),
            "run_id": run_id,
            "status": status,
            "step": step,
            "message": message,
            "data": dict(data or {}),
        }

        self.status_path.write_text(
            json.dumps(event, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

        return event

    def load(self) -> dict[str, Any]:
        if not self.status_path.exists():
            return {}

        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def load_events(self, limit: int = 80) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []

        rows: list[dict[str, Any]] = []

        for line in self.events_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

        return rows[-limit:]