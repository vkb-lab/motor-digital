from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SandboxAPIAuditLog:
    def __init__(self, path: str | Path = "memory/sandbox_api_adapter/requests.json") -> None:
        self.path = Path(path)

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []

    def append(self, item: Mapping[str, Any]) -> dict[str, Any]:
        rows = self.load()
        row = {
            "request_id": str(uuid4()),
            "created_at": utc_now_iso(),
            **dict(item),
        }

        rows.append(row)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return row
