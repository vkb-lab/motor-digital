from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventBus:
    def __init__(self, path: str | Path = "memory/control_plane/events.jsonl") -> None:
        self.path = Path(path)

    def emit(
        self,
        event_type: str,
        source: str,
        payload: Mapping[str, Any] | None = None,
        severity: str = "info",
    ) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        event = {
            "timestamp": utc_now_iso(),
            "event_type": event_type,
            "source": source,
            "severity": severity,
            "payload": dict(payload or {}),
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

        return event

    def read_events(self, limit: int = 100) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        rows: list[dict[str, Any]] = []

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                text = line.strip()
                if text:
                    rows.append(json.loads(text))

        return rows[-limit:]