# -*- coding: utf-8 -*-
"""K-Social AutoReporter.

Creates supervised operational reports from K-Social cockpit snapshots.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialAutoReporter:
    """Generates JSON and Markdown reports for K-Social operations."""

    def __init__(
        self,
        snapshot_path: Optional[Path] = None,
        reports_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.reports_dir = Path(reports_dir) if reports_dir else base_dir / "reports"
        self.snapshot_path = (
            Path(snapshot_path)
            if snapshot_path
            else self.reports_dir / "social_dashboard_snapshot.json"
        )
        self.json_report_path = self.reports_dir / "social_daily_report.json"
        self.md_report_path = self.reports_dir / "social_daily_report.md"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def load_snapshot(self) -> Dict[str, Any]:
        """Load dashboard snapshot safely."""

        if not self.snapshot_path.exists():
            return {
                "system": "K-Social Cockpit Snapshot",
                "snapshot_found": False,
                "total_operations": 0,
                "ready_for_review": 0,
                "blocked_operations": 0,
                "total_content_items": 0,
                "publication_permission": False,
                "external_api_used": False,
                "human_review_required": True,
                "operations": [],
            }

        with self.snapshot_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        data["snapshot_found"] = True
        return data

    def build_report(self) -> Dict[str, Any]:
        """Build structured daily report from snapshot."""

        snapshot = self.load_snapshot()
        operations = snapshot.get("operations", [])

        risks: List[str] = []
        next_actions: List[str] = []

        if snapshot.get("publication_permission") is not False:
            risks.append("Publication permission must remain blocked.")

        if snapshot.get("external_api_used") is not False:
            risks.append("External API usage detected. Review integration permissions.")

        if snapshot.get("blocked_operations", 0) > 0:
            risks.append("There are blocked social operations requiring review.")

        if snapshot.get("ready_for_review", 0) > 0:
            next_actions.append("Review approved-for-human-review social operations.")
        else:
            next_actions.append("Generate or update at least one supervised social operation.")

        if snapshot.get("total_content_items", 0) > 0:
            next_actions.append("Select top draft content items for human refinement.")

        next_actions.append("Keep auto-publishing disabled.")
        next_actions.append("Use reports as cockpit input, not as publishing authorization.")

        operation_summaries: List[Dict[str, Any]] = []

        for operation in operations:
            operation_summaries.append(
                {
                    "product": operation.get("product", "unknown"),
                    "market": operation.get("market", "unknown"),
                    "objective": operation.get("objective", "unknown"),
                    "audit_status": operation.get("audit_status", "unknown"),
                    "channels": operation.get("channels", []),
                    "content_items": operation.get("content_items", 0),
                    "human_review_required": operation.get("human_review_required", True),
                    "publication_permission": operation.get("publication_permission", False),
                }
            )

        report = {
            "system": "K-Social AutoReporter",
            "generated_at": self._now(),
            "snapshot_found": snapshot.get("snapshot_found", False),
            "summary": {
                "total_operations": snapshot.get("total_operations", 0),
                "ready_for_review": snapshot.get("ready_for_review", 0),
                "blocked_operations": snapshot.get("blocked_operations", 0),
                "total_content_items": snapshot.get("total_content_items", 0),
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
            },
            "risks": risks,
            "next_actions": next_actions,
            "operations": operation_summaries,
        }

        return report

    def save_json_report(self, report: Dict[str, Any]) -> Path:
        """Save report as JSON."""

        with self.json_report_path.open("w", encoding="utf-8-sig") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)

        return self.json_report_path

    def save_markdown_report(self, report: Dict[str, Any]) -> Path:
        """Save report as Markdown."""

        summary = report["summary"]
        lines: List[str] = []

        lines.append("# K-Social Daily Report")
        lines.append("")
        lines.append(f"Generated at: {report['generated_at']}")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total operations: {summary['total_operations']}")
        lines.append(f"- Ready for review: {summary['ready_for_review']}")
        lines.append(f"- Blocked operations: {summary['blocked_operations']}")
        lines.append(f"- Total content items: {summary['total_content_items']}")
        lines.append(f"- Human review required: {summary['human_review_required']}")
        lines.append(f"- Publication permission: {summary['publication_permission']}")
        lines.append(f"- External API used: {summary['external_api_used']}")
        lines.append("")
        lines.append("## Risks")
        lines.append("")

        if report["risks"]:
            for risk in report["risks"]:
                lines.append(f"- {risk}")
        else:
            lines.append("- No critical risk detected in this report.")

        lines.append("")
        lines.append("## Next actions")
        lines.append("")

        for action in report["next_actions"]:
            lines.append(f"- {action}")

        lines.append("")
        lines.append("## Operations")
        lines.append("")

        if not report["operations"]:
            lines.append("- No social operations found.")
        else:
            for operation in report["operations"]:
                lines.append(f"### {operation['product']}")
                lines.append("")
                lines.append(f"- Market: {operation['market']}")
                lines.append(f"- Objective: {operation['objective']}")
                lines.append(f"- Audit status: {operation['audit_status']}")
                lines.append(f"- Channels: {', '.join(operation['channels'])}")
                lines.append(f"- Content items: {operation['content_items']}")
                lines.append(f"- Human review required: {operation['human_review_required']}")
                lines.append(f"- Publication permission: {operation['publication_permission']}")
                lines.append("")

        lines.append("## Governance")
        lines.append("")
        lines.append("- Auto-publishing is blocked.")
        lines.append("- External APIs are blocked in this checkpoint.")
        lines.append("- Human review is mandatory.")
        lines.append("- This report is operational intelligence, not publishing approval.")
        lines.append("")

        self.md_report_path.write_text("\n".join(lines), encoding="utf-8")
        return self.md_report_path

    def run(self) -> Dict[str, Any]:
        """Build and save JSON plus Markdown reports."""

        report = self.build_report()
        self.save_json_report(report)
        self.save_markdown_report(report)
        return report


def main() -> None:
    reporter = SocialAutoReporter()
    report = reporter.run()

    print("K-Social AutoReporter completed.")
    print("JSON report:", reporter.json_report_path)
    print("Markdown report:", reporter.md_report_path)
    print("Total operations:", report["summary"]["total_operations"])
    print("Ready for review:", report["summary"]["ready_for_review"])
    print("Blocked operations:", report["summary"]["blocked_operations"])
    print("Publication permission:", report["summary"]["publication_permission"])


if __name__ == "__main__":
    main()
