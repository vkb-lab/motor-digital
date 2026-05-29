from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupervisorQueue:
    def __init__(self, path: str | Path = "memory/control_plane/supervisor_queue.json") -> None:
        self.path = Path(path)

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Supervisor queue corrompida: esperado lista")
        return data

    def save(self, rows: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def enqueue(
        self,
        task: Mapping[str, Any],
        reasons: list[str],
        requested_by: str,
    ) -> dict[str, Any]:
        rows = self.load()

        item = {
            "approval_id": str(uuid4()),
            "created_at": utc_now_iso(),
            "status": "pending_approval",
            "requested_by": requested_by,
            "reasons": reasons,
            "task": dict(task),
        }

        rows.append(item)
        self.save(rows)
        return item

    def approve(self, approval_id: str, reviewer: str) -> dict[str, Any]:
        rows = self.load()

        for item in rows:
            if item.get("approval_id") == approval_id:
                item["status"] = "approved"
                item["reviewer"] = reviewer
                item["reviewed_at"] = utc_now_iso()
                self.save(rows)
                return item

        raise KeyError(f"approval_id nao encontrado: {approval_id}")