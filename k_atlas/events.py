"""JSONL event logging for K-Atlas OS."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import EVENTS_FILE, ensure_dirs


def emit_event(event_type: str, payload: dict[str, Any] | None = None, path: Path = EVENTS_FILE) -> dict[str, Any]:
    ensure_dirs()
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "payload": payload or {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def read_events(limit: int = 50, path: Path = EVENTS_FILE) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    events: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"ts": "", "type": "invalid_event", "payload": {"raw": line}})
    return events

