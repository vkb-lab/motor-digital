# -*- coding: utf-8 -*-
"""K-Social Command Center.

Builds a consolidated operational snapshot for K-Social.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class SocialCommandCenter:
    """Aggregates K-Social operational state into one dashboard-ready object."""

    def __init__(
        self,
        social_dir: Optional[Path] = None,
        output_file: Optional[Path] = None,
    ) -> None:
        self.social_dir = Path(social_dir) if social_dir else Path(__file__).resolve().parents[1]
        self.reports_dir = self.social_dir / "reports"
        self.memory_dir = self.social_dir / "memory"
        self.packages_dir = self.reports_dir / "campaign_packages"

        self.output_file = (
            Path(output_file)
            if output_file
            else self.reports_dir / "social_command_center.json"
        )

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}

        try:
            with path.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

        if not isinstance(data, dict):
            return {}

        return data

    def build(self) -> Dict[str, Any]:
        dashboard = self._load_json(self.reports_dir / "social_dashboard_snapshot.json")
        daily_report = self._load_json(self.reports_dir / "social_daily_report.json")
        approval_queue = self._load_json(self.memory_dir / "social_approval_queue.json")
        refinement_queue = self._load_json(self.memory_dir / "social_content_refinement_queue.json")
        package_index = self._load_json(self.packages_dir / "campaign_package_index.json")
        package_approval = self._load_json(self.memory_dir / "campaign_package_approval_queue.json")

        command_center = {
            "system": "K-Social Command Center",
            "generated_at": self._now(),
            "status": "operational",
            "operations": {
                "total": int(dashboard.get("total_operations", 0)),
                "ready_for_review": int(dashboard.get("ready_for_review", 0)),
                "blocked": int(dashboard.get("blocked_operations", 0)),
                "content_items": int(dashboard.get("total_content_items", 0)),
            },
            "approval_queue": {
                "total": int(approval_queue.get("total_items", 0)),
                "pending": int(approval_queue.get("counts", {}).get("pending_human_review", 0)),
                "approved_for_refinement": int(approval_queue.get("counts", {}).get("approved_for_content_refinement", 0)),
                "needs_revision": int(approval_queue.get("counts", {}).get("needs_revision", 0)),
                "rejected": int(approval_queue.get("counts", {}).get("rejected", 0)),
            },
            "refinement_queue": {
                "total_tasks": int(refinement_queue.get("total_tasks", 0)),
                "pending": int(refinement_queue.get("counts", {}).get("pending_refinement", 0)),
                "in_progress": int(refinement_queue.get("counts", {}).get("in_progress", 0)),
                "done": int(refinement_queue.get("counts", {}).get("done", 0)),
                "blocked": int(refinement_queue.get("counts", {}).get("blocked", 0)),
            },
            "campaign_packages": {
                "total": int(package_index.get("total_packages", 0)),
                "recent": len(package_index.get("recent_packages", [])),
                "latest": package_index.get("latest_package", {}),
            },
            "package_approval": {
                "total": int(package_approval.get("total_items", 0)),
                "pending_final_review": int(package_approval.get("counts", {}).get("pending_final_review", 0)),
                "approved_for_manual_use": int(package_approval.get("counts", {}).get("approved_for_manual_use", 0)),
                "needs_package_revision": int(package_approval.get("counts", {}).get("needs_package_revision", 0)),
                "rejected": int(package_approval.get("counts", {}).get("rejected", 0)),
            },
            "daily_report": {
                "found": bool(daily_report),
                "risks": len(daily_report.get("risks", [])) if daily_report else 0,
                "next_actions": len(daily_report.get("next_actions", [])) if daily_report else 0,
            },
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "manual_use_only_after_final_approval": True,
            },
        }

        return command_center

    def save(self) -> Dict[str, Any]:
        command_center = self.build()

        self.output_file.write_text(
            json.dumps(command_center, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return command_center


def main() -> None:
    command_center = SocialCommandCenter()
    data = command_center.save()

    print("K-Social Command Center generated.")
    print("Output:", command_center.output_file)
    print("Operations:", data["operations"]["total"])
    print("Approval pending:", data["approval_queue"]["pending"])
    print("Refinement tasks:", data["refinement_queue"]["total_tasks"])
    print("Packages:", data["campaign_packages"]["total"])
    print("Manual approvals:", data["package_approval"]["approved_for_manual_use"])
    print("Auto publish:", data["governance"]["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
