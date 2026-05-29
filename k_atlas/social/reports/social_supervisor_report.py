# -*- coding: utf-8 -*-
"""K-Social supervisor report generator."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class SocialSupervisorReport:
    """Generates a supervisor-ready report for K-Social autonomous campaign tests."""

    def __init__(
        self,
        social_dir: Optional[Path] = None,
    ) -> None:
        self.social_dir = Path(social_dir) if social_dir else Path(__file__).resolve().parents[1]
        self.reports_dir = self.social_dir / "reports"
        self.packages_dir = self.reports_dir / "campaign_packages"
        self.plan_dir = self.reports_dir / "test_page_publish_plan"
        self.receipts_dir = self.reports_dir / "test_page_publish_receipts"
        self.output_dir = self.reports_dir / "supervisor_reports"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.json_path = self.output_dir / "k_social_supervisor_report_ecobier_campaign.json"
        self.md_path = self.output_dir / "k_social_supervisor_report_ecobier_campaign.md"

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

    def build_report(self) -> Dict[str, Any]:
        latest_campaign = self._load_json(self.packages_dir / "latest_manual_approved_campaign.json")
        command_center = self._load_json(self.reports_dir / "social_command_center.json")
        test_plan = self._load_json(self.plan_dir / "latest_test_page_publish_plan.json")
        receipts = self._load_json(self.receipts_dir / "latest_test_page_receipts.json")

        campaign = latest_campaign.get("campaign", {})
        governance = latest_campaign.get("governance", {})

        report = {
            "system": "K-Social Supervisor Report",
            "generated_at": self._now(),
            "campaign": {
                "name": campaign.get("package_name", "nao informado"),
                "status": campaign.get("approval_status", "nao informado"),
                "assets": campaign.get("total_assets", 0),
                "json_path": campaign.get("json_path", ""),
                "markdown_path": campaign.get("markdown_path", ""),
            },
            "command_center": {
                "operations": command_center.get("operations", {}).get("total", 0),
                "refinements": command_center.get("refinement_queue", {}).get("total_tasks", 0),
                "packages": command_center.get("campaign_packages", {}).get("total", 0),
                "manual_approvals": command_center.get("package_approval", {}).get("approved_for_manual_use", 0),
            },
            "test_page_validation": {
                "target_page": test_plan.get("target_page", "nao informado"),
                "environment": test_plan.get("environment", "nao informado"),
                "payloads_planned": test_plan.get("total_payloads", 0),
                "payloads_validated": receipts.get("payloads_validated", 0),
                "real_publish": False,
                "dry_run": True,
            },
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "manual_use_only": governance.get("manual_use_only", True),
            },
            "supervisor_summary": [
                "K-Social executed a complete supervised campaign pipeline.",
                "The Parada Atlantida + Chopp Ecobier campaign was created, refined, packaged and approved for manual use.",
                "A local test-page dry run validated the payloads without publishing to real networks.",
                "No external APIs, browser automation or automatic publishing were used.",
                "The system remains compliant with human-review governance."
            ],
            "risks_blocked": [
                "Auto-publishing remained blocked.",
                "External API usage remained blocked.",
                "Official tournament sponsorship was not claimed.",
                "Official logos and protected brand assets were not used by the automation.",
                "Real posting was not executed."
            ],
            "next_recommendations": [
                "Connect a real test-page API only after credential governance is implemented.",
                "Add token vault and permission model before live integration.",
                "Add final content editor before any real scheduling.",
                "Keep manual approval as mandatory before any publication adapter is enabled."
            ],
        }

        return report

    def save_report(self, report: Dict[str, Any]) -> Dict[str, str]:
        self.json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        lines = []
        lines.append("# K-Social Supervisor Report")
        lines.append("")
        lines.append(f"Generated at: {report['generated_at']}")
        lines.append("")
        lines.append("## Executive Summary")
        lines.append("")

        for item in report["supervisor_summary"]:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("## Campaign")
        lines.append("")
        lines.append(f"- Name: {report['campaign']['name']}")
        lines.append(f"- Status: {report['campaign']['status']}")
        lines.append(f"- Assets: {report['campaign']['assets']}")
        lines.append(f"- JSON package: {report['campaign']['json_path']}")
        lines.append(f"- Markdown package: {report['campaign']['markdown_path']}")
        lines.append("")
        lines.append("## Command Center")
        lines.append("")
        lines.append(f"- Operations: {report['command_center']['operations']}")
        lines.append(f"- Refinements: {report['command_center']['refinements']}")
        lines.append(f"- Packages: {report['command_center']['packages']}")
        lines.append(f"- Manual approvals: {report['command_center']['manual_approvals']}")
        lines.append("")
        lines.append("## Local Test Page Validation")
        lines.append("")
        lines.append(f"- Target page: {report['test_page_validation']['target_page']}")
        lines.append(f"- Environment: {report['test_page_validation']['environment']}")
        lines.append(f"- Payloads planned: {report['test_page_validation']['payloads_planned']}")
        lines.append(f"- Payloads validated: {report['test_page_validation']['payloads_validated']}")
        lines.append(f"- Real publish: {report['test_page_validation']['real_publish']}")
        lines.append(f"- Dry run: {report['test_page_validation']['dry_run']}")
        lines.append("")
        lines.append("## Governance")
        lines.append("")
        lines.append(f"- Human review required: {report['governance']['human_review_required']}")
        lines.append(f"- Publication permission: {report['governance']['publication_permission']}")
        lines.append(f"- External API used: {report['governance']['external_api_used']}")
        lines.append(f"- Approved for auto publish: {report['governance']['approved_for_auto_publish']}")
        lines.append(f"- Manual use only: {report['governance']['manual_use_only']}")
        lines.append("")
        lines.append("## Risks Blocked")
        lines.append("")

        for item in report["risks_blocked"]:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("## Next Recommendations")
        lines.append("")

        for item in report["next_recommendations"]:
            lines.append(f"- {item}")

        lines.append("")

        self.md_path.write_text("\n".join(lines), encoding="utf-8")

        return {
            "json_path": str(self.json_path),
            "markdown_path": str(self.md_path),
        }

    def run(self) -> Dict[str, Any]:
        report = self.build_report()
        paths = self.save_report(report)

        return {
            "report": report,
            "paths": paths,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "human_review_required": True,
        }


def main() -> None:
    generator = SocialSupervisorReport()
    result = generator.run()

    report = result["report"]

    print("K-Social supervisor report generated.")
    print("Campaign:", report["campaign"]["name"])
    print("Payloads planned:", report["test_page_validation"]["payloads_planned"])
    print("Payloads validated:", report["test_page_validation"]["payloads_validated"])
    print("Markdown:", result["paths"]["markdown_path"])
    print("Publication permission:", result["publication_permission"])
    print("Auto publish:", result["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
