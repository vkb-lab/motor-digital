from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpdateVerificationGate:
    def __init__(
        self,
        queue_path: str | Path = "live/update_intake_queue/update_queue.json",
        live_dir: str | Path = "live/update_verification_gate",
        reports_dir: str | Path = "reports/update_verification_gate",
    ) -> None:
        self.queue_path = Path(queue_path)
        self.live_dir = Path(live_dir)
        self.reports_dir = Path(reports_dir)
        self.verified_path = self.live_dir / "verified_updates.json"

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

    def verify_item(self, item: dict[str, Any]) -> dict[str, Any]:
        reasons: list[str] = []
        installer_name = str(item.get("installer_name", ""))

        if item.get("status") != "queued_for_verification":
            reasons.append("invalid_status")

        if not installer_name.startswith("K_ATLAS_"):
            reasons.append("installer_prefix_required")

        if not installer_name.endswith(".ps1"):
            reasons.append("ps1_installer_required")

        if item.get("automatic_public_access_allowed") is True:
            reasons.append("public_access_blocked")

        return {
            "ok": len(reasons) == 0,
            "update_id": item.get("update_id"),
            "installer_name": installer_name,
            "status": "verified_for_supervised_apply" if not reasons else "blocked_by_verification_gate",
            "reasons": reasons or ["verification_passed"],
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "external_side_effects": "none",
            "source_item": item,
        }

    def build_verified_queue(self) -> dict[str, Any]:
        queue = self.load_list(self.queue_path)
        existing = self.load_list(self.verified_path)
        existing_ids = {item.get("update_id") for item in existing}

        created: list[dict[str, Any]] = []
        for item in queue:
            if item.get("update_id") in existing_ids:
                continue
            result = self.verify_item(item)
            created.append(result)

        existing.extend(created)
        self.save_list(self.verified_path, existing)

        report = {
            "ok": True,
            "checkpoint": "114",
            "name": "Update Verification Gate",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "intake_total": len(queue),
                "verified_total": len(existing),
                "created": len(created),
                "ready_for_supervised_apply": len([x for x in existing if x.get("status") == "verified_for_supervised_apply"]),
                "automatic_execution_allowed": False,
            },
            "verified_updates": existing,
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_update_verification_gate.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return report
