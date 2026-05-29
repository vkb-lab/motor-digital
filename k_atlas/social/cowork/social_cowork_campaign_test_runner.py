# -*- coding: utf-8 -*-
"""K-Social Cowork autonomous test runner.

Runs the approved campaign through local test-page validation and supervisor reporting.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from k_atlas.social.analytics.social_command_center import SocialCommandCenter
from k_atlas.social.campaign_factory.social_campaign_package_cleanup import SocialCampaignPackageCleanup
from k_atlas.social.live.social_test_page_publisher import SocialTestPagePublisher
from k_atlas.social.reports.social_supervisor_report import SocialSupervisorReport


class SocialCoworkCampaignTestRunner:
    """Executes the complete local Cowork test for an approved campaign."""

    def __init__(
        self,
        social_dir: Optional[Path] = None,
    ) -> None:
        self.social_dir = Path(social_dir) if social_dir else Path(__file__).resolve().parents[1]
        self.reports_dir = self.social_dir / "reports"
        self.output_dir = self.reports_dir / "cowork"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def run(
        self,
        product_filter: str = "Parada Atlantida + Chopp Ecobier",
    ) -> Dict[str, Any]:
        cleanup = SocialCampaignPackageCleanup(
            packages_dir=self.reports_dir / "campaign_packages"
        )
        cleanup_index = cleanup.run(product_filter=product_filter)

        publisher = SocialTestPagePublisher(social_dir=self.social_dir)
        publish_result = publisher.run()

        command_center = SocialCommandCenter(
            social_dir=self.social_dir,
            output_file=self.reports_dir / "social_command_center.json",
        ).save()

        supervisor_report = SocialSupervisorReport(
            social_dir=self.social_dir,
        ).run()

        result = {
            "system": "K-Social Cowork Campaign Test Runner",
            "generated_at": self._now(),
            "product_filter": product_filter,
            "latest_campaign": cleanup_index.get("latest_manual_approved", {}),
            "publish_result": publish_result,
            "command_center": {
                "operations": command_center["operations"]["total"],
                "refinements": command_center["refinement_queue"]["total_tasks"],
                "packages": command_center["campaign_packages"]["total"],
                "manual_approvals": command_center["package_approval"]["approved_for_manual_use"],
            },
            "supervisor_report": supervisor_report["paths"],
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "human_review_required": True,
            "dry_run": True,
        }

        output_path = self.output_dir / "latest_cowork_campaign_test_summary.json"
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return result


def main() -> None:
    runner = SocialCoworkCampaignTestRunner()
    result = runner.run()

    print("K-Social Cowork campaign test completed.")
    print("Campaign:", result["latest_campaign"].get("package_name", "none"))
    print("Payloads planned:", result["publish_result"]["payloads_planned"])
    print("Payloads validated:", result["publish_result"]["payloads_validated"])
    print("Supervisor report:", result["supervisor_report"]["markdown_path"])
    print("Dry run:", result["dry_run"])
    print("Publication permission:", result["publication_permission"])
    print("Auto publish:", result["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
