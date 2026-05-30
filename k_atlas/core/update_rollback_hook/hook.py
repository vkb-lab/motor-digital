from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpdateRollbackHook:
    def __init__(
        self,
        memory_dir: str | Path = "memory/update_rollback_hook",
        reports_dir: str | Path = "reports/update_rollback_hook",
    ) -> None:
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.hook_manifest_path = self.memory_dir / "rollback_hooks.json"

    def load_hooks(self) -> list[dict[str, Any]]:
        if not self.hook_manifest_path.exists():
            return []
        try:
            data = json.loads(self.hook_manifest_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_hooks(self, hooks: list[dict[str, Any]]) -> None:
        self.hook_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.hook_manifest_path.write_text(json.dumps(hooks, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def create_hook(self, source: str = "update_pipeline") -> dict[str, Any]:
        hook = {
            "rollback_hook_id": str(uuid4()),
            "created_at": utc_now(),
            "source": source,
            "status": "rollback_hook_registered",
            "rollback_available": True,
            "manual_approval_required": True,
            "automatic_rollback_allowed": False,
        }
        hooks = self.load_hooks()
        hooks.append(hook)
        self.save_hooks(hooks)

        report = {
            "ok": True,
            "checkpoint": "116",
            "name": "Update Rollback Hook",
            "generated_at": utc_now(),
            "status": "operational",
            "latest_hook": hook,
            "summary": {
                "hooks_total": len(hooks),
                "automatic_rollback_allowed": False,
            },
        }
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_update_rollback_hook.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return report
