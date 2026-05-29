from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SENSITIVE_KEY_PARTS = ("token", "secret", "password", "api_key", "access_key")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_for_audit(value: Any) -> Any:
    if isinstance(value, Mapping):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                clean[key_text] = "[REDACTED]"
            else:
                clean[key_text] = sanitize_for_audit(item)
        return clean

    if isinstance(value, list):
        return [sanitize_for_audit(item) for item in value]

    if isinstance(value, tuple):
        return [sanitize_for_audit(item) for item in value]

    return value


class AuditLog:
    def __init__(self, path: str | Path = "reports/social_publishing_gateway_audit.jsonl") -> None:
        self.path = Path(path)

    def write_event(
        self,
        action: str,
        status: str,
        actor: str,
        payload: Mapping[str, Any] | None = None,
        reasons: list[str] | None = None,
    ) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": utc_now_iso(),
            "action": action,
            "status": status,
            "actor": actor,
            "reasons": reasons or [],
            "payload": sanitize_for_audit(payload or {}),
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

        return event

    def read_events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        events: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                text = line.strip()
                if text:
                    events.append(json.loads(text))
        return events