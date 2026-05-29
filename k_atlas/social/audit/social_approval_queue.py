# -*- coding: utf-8 -*-
"""K-Social human approval queue.

This module creates and manages a local human approval queue for social operations.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialApprovalQueue:
    """Builds and updates a supervised human approval queue."""

    IGNORED_REPORT_FILES = {
        "social_dashboard_snapshot.json",
        "social_daily_report.json",
    }

    VALID_DECISIONS = {
        "pending_human_review",
        "approved_for_content_refinement",
        "needs_revision",
        "rejected",
    }

    REQUIRED_OPERATION_KEYS = {
        "system",
        "operation_status",
        "audience",
        "creative_brief",
        "campaign",
        "audit",
    }

    def __init__(
        self,
        reports_dir: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.reports_dir = Path(reports_dir) if reports_dir else base_dir / "reports"
        self.memory_dir = Path(memory_dir) if memory_dir else base_dir / "memory"
        self.queue_file = self.memory_dir / "social_approval_queue.json"

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_json(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return None

        if not isinstance(data, dict):
            return None

        return data

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def _is_operation_report(self, data: Dict[str, Any]) -> bool:
        missing = self.REQUIRED_OPERATION_KEYS.difference(set(data.keys()))
        if missing:
            return False

        if data.get("publication_permission") is not False:
            return False

        if data.get("external_api_used") is not False:
            return False

        if data.get("human_review_required") is not True:
            return False

        if not isinstance(data.get("campaign", {}), dict):
            return False

        if not isinstance(data.get("audit", {}), dict):
            return False

        return True

    def _operation_paths(self) -> List[Path]:
        paths: List[Path] = []

        for path in sorted(self.reports_dir.glob("*.json")):
            if path.name in self.IGNORED_REPORT_FILES:
                continue

            data = self._load_json(path)
            if not data:
                continue

            if self._is_operation_report(data):
                paths.append(path)

        return paths

    def _build_item(self, path: Path, operation: Dict[str, Any]) -> Dict[str, Any]:
        audience = operation.get("audience", {})
        creative_brief = operation.get("creative_brief", {})
        campaign = operation.get("campaign", {})
        audit = operation.get("audit", {})
        metadata = operation.get("request_metadata", {})

        approval_status = metadata.get("approval_status", "pending_human_review")

        if approval_status not in self.VALID_DECISIONS:
            approval_status = "pending_human_review"

        content_calendar = campaign.get("content_calendar", [])
        content_items = len(content_calendar) if isinstance(content_calendar, list) else 0

        return {
            "source_file": path.name,
            "product": audience.get("product", creative_brief.get("product", "produto nao informado")),
            "market": audience.get("market", "mercado nao informado"),
            "objective": campaign.get("objective", creative_brief.get("objective", "objetivo nao informado")),
            "audit_status": audit.get("audit_status", "unknown"),
            "approval_status": approval_status,
            "channels": campaign.get("channels", []),
            "duration_days": campaign.get("duration_days", 0),
            "content_items": content_items,
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
        }

    def build_queue(self) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        for path in self._operation_paths():
            operation = self._load_json(path)
            if not operation:
                continue

            items.append(self._build_item(path, operation))

        counts = {
            "pending_human_review": 0,
            "approved_for_content_refinement": 0,
            "needs_revision": 0,
            "rejected": 0,
        }

        for item in items:
            status = item.get("approval_status", "pending_human_review")
            if status in counts:
                counts[status] += 1

        return {
            "system": "K-Social Human Approval Queue",
            "generated_at": self._now(),
            "total_items": len(items),
            "counts": counts,
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "items": items,
        }

    def save_queue(self) -> Dict[str, Any]:
        queue = self.build_queue()
        self._save_json(self.queue_file, queue)
        return queue

    def update_decision(
        self,
        source_file: str,
        decision: str,
        reviewer: str = "K-Atlas Operator",
        notes: str = "",
    ) -> Dict[str, Any]:
        if decision not in self.VALID_DECISIONS:
            raise ValueError("Invalid approval decision.")

        if decision == "approved_for_auto_publish":
            raise ValueError("Auto-publish approval is blocked.")

        operation_path = self.reports_dir / source_file

        if not operation_path.exists():
            raise FileNotFoundError(f"Operation file not found: {source_file}")

        operation = self._load_json(operation_path)

        if not operation or not self._is_operation_report(operation):
            raise ValueError("Invalid social operation report.")

        metadata = operation.get("request_metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        metadata["approval_status"] = decision
        metadata["last_reviewed_at"] = self._now()
        metadata["last_reviewer"] = reviewer
        metadata["last_review_notes"] = notes

        operation["request_metadata"] = metadata

        events = operation.get("approval_events", [])
        if not isinstance(events, list):
            events = []

        events.append(
            {
                "created_at": self._now(),
                "reviewer": reviewer,
                "decision": decision,
                "notes": notes,
                "publication_permission": False,
                "approved_for_auto_publish": False,
            }
        )

        operation["approval_events"] = events
        operation["publication_permission"] = False
        operation["external_api_used"] = False
        operation["human_review_required"] = True

        self._save_json(operation_path, operation)
        return self.save_queue()


def main() -> None:
    queue_manager = SocialApprovalQueue()
    queue = queue_manager.save_queue()

    print("K-Social approval queue generated.")
    print("Queue file:", queue_manager.queue_file)
    print("Total items:", queue["total_items"])
    print("Pending:", queue["counts"]["pending_human_review"])
    print("Approved for refinement:", queue["counts"]["approved_for_content_refinement"])
    print("Needs revision:", queue["counts"]["needs_revision"])
    print("Rejected:", queue["counts"]["rejected"])
    print("Publication permission:", queue["publication_permission"])


if __name__ == "__main__":
    main()
