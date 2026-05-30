from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpdateApplyRunner:
    def __init__(
        self,
        verified_path: str | Path = "live/update_verification_gate/verified_updates.json",
        memory_dir: str | Path = "memory/update_apply_runner",
        reports_dir: str | Path = "reports/update_apply_runner",
    ) -> None:
        self.verified_path = Path(verified_path)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.apply_manifest_path = self.memory_dir / "apply_manifest.json"

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def dry_run(self) -> dict[str, Any]:
        verified = self.load_list(self.verified_path)
        ready = [item for item in verified if item.get("status") == "verified_for_supervised_apply"]

        report = {
            "ok": True,
            "checkpoint": "115",
            "name": "Update Apply Runner",
            "generated_at": utc_now(),
            "status": "dry_run_completed",
            "summary": {
                "ready_updates": len(ready),
                "real_execution_enabled": False,
                "automatic_execution_allowed": False,
                "external_side_effects": "none",
            },
            "plan": [
                {
                    "update_id": item.get("update_id"),
                    "installer_name": item.get("installer_name"),
                    "planned_action": "await_human_supervised_apply",
                    "ready": True,
                }
                for item in ready
            ],
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_update_apply_runner.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return report

    def record_supervised_apply_ready(self) -> dict[str, Any]:
        dry = self.dry_run()
        manifest = self.load_list(self.apply_manifest_path)
        item = {
            "apply_record_id": str(uuid4()),
            "created_at": utc_now(),
            "status": "supervised_apply_ready",
            "dry_run": dry,
            "rollback_hook_required": True,
            "real_execution_enabled": False,
            "automatic_execution_allowed": False,
        }
        manifest.append(item)
        self.save_list(self.apply_manifest_path, manifest)
        return item
