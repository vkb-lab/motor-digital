# -*- coding: utf-8 -*-
"""K-Social campaign package cleanup and latest selector.

Selects the latest manually approved campaign package and creates clean summary files.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialCampaignPackageCleanup:
    """Creates a clean latest-approved campaign package pointer."""

    INDEX_FILE_NAME = "campaign_package_cleanup_index.json"
    LATEST_JSON_FILE_NAME = "latest_manual_approved_campaign.json"
    LATEST_MD_FILE_NAME = "latest_manual_approved_campaign.md"

    IGNORED_JSON_FILES = {
        "campaign_package_index.json",
        "campaign_package_cleanup_index.json",
        "latest_manual_approved_campaign.json",
    }

    def __init__(
        self,
        packages_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.packages_dir = (
            Path(packages_dir)
            if packages_dir
            else base_dir / "reports" / "campaign_packages"
        )
        self.packages_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.packages_dir / self.INDEX_FILE_NAME
        self.latest_json_file = self.packages_dir / self.LATEST_JSON_FILE_NAME
        self.latest_md_file = self.packages_dir / self.LATEST_MD_FILE_NAME

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

    def _is_valid_package(self, package: Dict[str, Any]) -> bool:
        if package.get("system") != "K-Social Campaign Package Exporter":
            return False

        governance = package.get("governance", {})
        if not isinstance(governance, dict):
            return False

        if governance.get("publication_permission") is not False:
            return False

        if governance.get("external_api_used") is not False:
            return False

        if governance.get("human_review_required") is not True:
            return False

        if governance.get("approved_for_auto_publish") is not False:
            return False

        return True

    def _approval_status(self, package: Dict[str, Any]) -> str:
        metadata = package.get("package_metadata", {})
        if not isinstance(metadata, dict):
            return "pending_final_review"

        return str(metadata.get("final_approval_status", "pending_final_review"))

    def _approval_time(self, package: Dict[str, Any]) -> str:
        metadata = package.get("package_metadata", {})
        if isinstance(metadata, dict):
            reviewed = metadata.get("last_reviewed_at", "")
            if reviewed:
                return str(reviewed)

        return str(package.get("generated_at", ""))

    def _markdown_pair(self, json_path: Path) -> str:
        md_path = json_path.with_suffix(".md")
        if md_path.exists():
            return str(md_path)
        return ""

    def _matches_filter(self, package: Dict[str, Any], product_filter: str) -> bool:
        if not product_filter:
            return True

        searchable = " ".join(
            [
                str(package.get("package_name", "")),
                str(package.get("product_filter", "")),
                str(package.get("owner", "")),
            ]
        ).lower()

        return product_filter.lower() in searchable

    def load_packages(self, product_filter: str = "") -> List[Dict[str, Any]]:
        """Load valid campaign package records."""

        records: List[Dict[str, Any]] = []

        for path in sorted(self.packages_dir.glob("*.json")):
            if path.name in self.IGNORED_JSON_FILES:
                continue

            package = self._load_json(path)
            if not package:
                continue

            if not self._is_valid_package(package):
                continue

            if not self._matches_filter(package, product_filter):
                continue

            records.append(
                {
                    "file_name": path.name,
                    "json_path": str(path),
                    "markdown_path": self._markdown_pair(path),
                    "package_name": package.get("package_name", "pacote sem nome"),
                    "product_filter": package.get("product_filter", ""),
                    "owner": package.get("owner", "K-Atlas Operator"),
                    "generated_at": package.get("generated_at", ""),
                    "approval_status": self._approval_status(package),
                    "approval_time": self._approval_time(package),
                    "total_assets": int(package.get("total_assets", 0)),
                    "package": package,
                }
            )

        return records

    def build_cleanup_index(self, product_filter: str = "") -> Dict[str, Any]:
        """Build cleanup index and latest approved package pointer."""

        packages = self.load_packages(product_filter=product_filter)

        approved = [
            item
            for item in packages
            if item["approval_status"] == "approved_for_manual_use"
        ]

        approved = sorted(
            approved,
            key=lambda item: item.get("approval_time", ""),
            reverse=True,
        )

        latest = approved[0] if approved else {}
        archived_approved = approved[1:] if len(approved) > 1 else []

        index = {
            "system": "K-Social Campaign Package Cleanup",
            "generated_at": self._now(),
            "packages_dir": str(self.packages_dir),
            "product_filter": product_filter,
            "total_valid_packages": len(packages),
            "total_manual_approved": len(approved),
            "latest_manual_approved": self._safe_record(latest),
            "archived_manual_approved": [
                self._safe_record(item)
                for item in archived_approved
            ],
            "pending_or_other_packages": [
                self._safe_record(item)
                for item in packages
                if item["approval_status"] != "approved_for_manual_use"
            ],
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "manual_use_only": True,
            },
        }

        return index

    def _safe_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        if not record:
            return {}

        return {
            "file_name": record.get("file_name", ""),
            "json_path": record.get("json_path", ""),
            "markdown_path": record.get("markdown_path", ""),
            "package_name": record.get("package_name", ""),
            "product_filter": record.get("product_filter", ""),
            "owner": record.get("owner", ""),
            "generated_at": record.get("generated_at", ""),
            "approval_status": record.get("approval_status", ""),
            "approval_time": record.get("approval_time", ""),
            "total_assets": record.get("total_assets", 0),
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "manual_use_only": True,
        }

    def save_latest_files(self, index: Dict[str, Any]) -> None:
        """Save latest approved campaign as clean JSON and Markdown."""

        latest = index.get("latest_manual_approved", {})

        latest_payload = {
            "system": "K-Social Latest Manual Approved Campaign",
            "generated_at": self._now(),
            "latest_found": bool(latest),
            "campaign": latest,
            "governance": index["governance"],
        }

        self.latest_json_file.write_text(
            json.dumps(latest_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        lines: List[str] = []
        lines.append("# K-Social Latest Manual Approved Campaign")
        lines.append("")
        lines.append(f"Generated at: {latest_payload['generated_at']}")
        lines.append("")

        if not latest:
            lines.append("No manually approved campaign package found.")
            lines.append("")
        else:
            lines.append("## Campaign")
            lines.append("")
            lines.append(f"- Package name: {latest.get('package_name', '')}")
            lines.append(f"- Product filter: {latest.get('product_filter', '')}")
            lines.append(f"- Assets: {latest.get('total_assets', 0)}")
            lines.append(f"- Approval status: {latest.get('approval_status', '')}")
            lines.append(f"- Approval time: {latest.get('approval_time', '')}")
            lines.append(f"- JSON path: {latest.get('json_path', '')}")
            lines.append(f"- Markdown path: {latest.get('markdown_path', '')}")
            lines.append("")

        lines.append("## Governance")
        lines.append("")
        lines.append("- Human review required: True")
        lines.append("- Publication permission: False")
        lines.append("- External API used: False")
        lines.append("- Approved for auto publish: False")
        lines.append("- Manual use only: True")
        lines.append("")

        self.latest_md_file.write_text("\n".join(lines), encoding="utf-8")

    def run(self, product_filter: str = "") -> Dict[str, Any]:
        """Build, save and return cleanup index."""

        index = self.build_cleanup_index(product_filter=product_filter)

        self.index_file.write_text(
            json.dumps(index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.save_latest_files(index)

        return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean K-Social campaign package history.")
    parser.add_argument("--product-filter", default="")
    args = parser.parse_args()

    cleanup = SocialCampaignPackageCleanup()
    index = cleanup.run(product_filter=args.product_filter)

    latest = index.get("latest_manual_approved", {})

    print("K-Social campaign package cleanup completed.")
    print("Total valid packages:", index["total_valid_packages"])
    print("Manual approved:", index["total_manual_approved"])
    print("Latest:", latest.get("package_name", "none"))
    print("Latest JSON:", cleanup.latest_json_file)
    print("Auto publish:", index["governance"]["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
