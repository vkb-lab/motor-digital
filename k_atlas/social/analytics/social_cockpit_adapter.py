# -*- coding: utf-8 -*-
"""Cockpit adapter for K-Social.

This module converts supervised social operation reports into dashboard-ready JSON.
It does not publish content, does not use external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialCockpitAdapter:
    """Builds dashboard snapshots from K-Social operation reports."""

    IGNORED_REPORT_FILES = {
        "social_dashboard_snapshot.json",
        "social_daily_report.json",
        "social_approval_queue.json",
    }

    REQUIRED_OPERATION_KEYS = {
        "system",
        "operation_status",
        "audience",
        "creative_brief",
        "campaign",
        "audit",
    }

    APPROVAL_STATUSES = {
        "pending_human_review",
        "approved_for_content_refinement",
        "needs_revision",
        "rejected",
    }

    def __init__(
        self,
        reports_dir: Optional[Path] = None,
        output_file: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.reports_dir = Path(reports_dir) if reports_dir else base_dir / "reports"
        self.output_file = Path(output_file) if output_file else self.reports_dir / "social_dashboard_snapshot.json"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

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

    def _is_operation_report(self, data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False

        missing_keys = self.REQUIRED_OPERATION_KEYS.difference(set(data.keys()))
        if missing_keys:
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

    def _get_approval_status(self, operation: Dict[str, Any]) -> str:
        metadata = operation.get("request_metadata", {})
        if not isinstance(metadata, dict):
            return "pending_human_review"

        status = metadata.get("approval_status", "pending_human_review")
        if status not in self.APPROVAL_STATUSES:
            return "pending_human_review"

        return status

    def load_reports(self) -> List[Dict[str, Any]]:
        """Load only valid operation reports from reports_dir."""

        reports: List[Dict[str, Any]] = []

        for path in sorted(self.reports_dir.glob("*.json")):
            if path.name in self.IGNORED_REPORT_FILES:
                continue

            data = self._load_json(path)
            if not data:
                continue

            if self._is_operation_report(data):
                reports.append(
                    {
                        "file": path.name,
                        "data": data,
                    }
                )

        return reports

    def build_snapshot(self) -> Dict[str, Any]:
        reports = self.load_reports()

        operations: List[Dict[str, Any]] = []
        total_content_items = 0
        blocked_operations = 0
        ready_for_review = 0

        approval_counts = {
            "pending_human_review": 0,
            "approved_for_content_refinement": 0,
            "needs_revision": 0,
            "rejected": 0,
        }

        for report in reports:
            data = report["data"]
            campaign = data.get("campaign", {})
            audit = data.get("audit", {})
            audience = data.get("audience", {})
            creative_brief = data.get("creative_brief", {})

            content_calendar = campaign.get("content_calendar", [])
            content_count = len(content_calendar) if isinstance(content_calendar, list) else 0
            total_content_items += content_count

            audit_status = audit.get("audit_status", "unknown")
            approval_status = self._get_approval_status(data)

            if approval_status in approval_counts:
                approval_counts[approval_status] += 1

            if audit_status == "blocked":
                blocked_operations += 1

            if audit_status == "approved_for_human_review":
                ready_for_review += 1

            operations.append(
                {
                    "source_file": report["file"],
                    "product": audience.get("product", creative_brief.get("product", "produto nao informado")),
                    "market": audience.get("market", "mercado nao informado"),
                    "objective": campaign.get("objective", creative_brief.get("objective", "objetivo nao informado")),
                    "operation_status": data.get("operation_status", "unknown"),
                    "audit_status": audit_status,
                    "approval_status": approval_status,
                    "channels": campaign.get("channels", []),
                    "duration_days": campaign.get("duration_days", 0),
                    "content_items": content_count,
                    "human_review_required": data.get("human_review_required", True),
                    "publication_permission": data.get("publication_permission", False),
                    "external_api_used": data.get("external_api_used", False),
                    "approved_for_auto_publish": False,
                }
            )

        snapshot = {
            "system": "K-Social Cockpit Snapshot",
            "generated_at": self._now(),
            "reports_dir": str(self.reports_dir),
            "total_operations": len(operations),
            "ready_for_review": ready_for_review,
            "blocked_operations": blocked_operations,
            "total_content_items": total_content_items,
            "approval_counts": approval_counts,
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "approved_for_auto_publish": False,
            "operations": operations,
        }

        return snapshot

    def save_snapshot(self) -> Dict[str, Any]:
        snapshot = self.build_snapshot()

        with self.output_file.open("w", encoding="utf-8") as file:
            json.dump(snapshot, file, ensure_ascii=False, indent=2)

        return snapshot


def main() -> None:
    adapter = SocialCockpitAdapter()
    snapshot = adapter.save_snapshot()

    print("Snapshot gerado em:", adapter.output_file)
    print("Operacoes:", snapshot["total_operations"])
    print("Prontas para revisao:", snapshot["ready_for_review"])
    print("Bloqueadas:", snapshot["blocked_operations"])
    print("Itens de conteudo:", snapshot["total_content_items"])
    print("Pendentes:", snapshot["approval_counts"]["pending_human_review"])
    print("Aprovadas para refinamento:", snapshot["approval_counts"]["approved_for_content_refinement"])
    print("Precisam revisao:", snapshot["approval_counts"]["needs_revision"])
    print("Rejeitadas:", snapshot["approval_counts"]["rejected"])
    print("Publicacao automatica:", snapshot["publication_permission"])


if __name__ == "__main__":
    main()
