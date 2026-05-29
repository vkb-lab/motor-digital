from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SystemState:
    def __init__(self, path: str | Path = "memory/control_plane/system_state.json") -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "system": "K-Atlas OS",
                "status": "initialized",
                "updated_at": utc_now_iso(),
                "modules": {},
            }

        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = dict(state)
        data["updated_at"] = utc_now_iso()
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def set_module_status(self, module_name: str, status: str, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        state = self.load()
        modules = dict(state.get("modules", {}))
        modules[module_name] = {
            "status": status,
            "metadata": dict(metadata or {}),
            "updated_at": utc_now_iso(),
        }
        state["modules"] = modules
        self.save(state)
        return state