"""Small JSON-backed operational memory store."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import MEMORY_DIR, ensure_dirs


class MemoryStore:
    def __init__(self, path: Path | None = None) -> None:
        ensure_dirs()
        self.path = path or (MEMORY_DIR / "operational_memory.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"items": []})

    def _read(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {"items": []}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, key: str, value: Any, tags: list[str] | None = None) -> dict[str, Any]:
        data = self._read()
        item = {
            "key": key,
            "value": value,
            "tags": tags or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data.setdefault("items", []).append(item)
        self._write(data)
        return item

    def all(self) -> list[dict[str, Any]]:
        return list(self._read().get("items", []))

    def find(self, key: str) -> list[dict[str, Any]]:
        return [item for item in self.all() if item.get("key") == key]

