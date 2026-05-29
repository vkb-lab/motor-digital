# -*- coding: utf-8 -*-
"""K-Social campaign package indexer.

Creates a clean index for exported campaign packages.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialCampaignPackageIndexer:
    """Builds a clean index for campaign packages."""

    INDEX_FILE_NAME = "campaign_package_index.json"

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

    def _is_campaign_package(self, data: Dict[str, Any]) -> bool:
        if data.get("system") != "K-Social Campaign Package Exporter":
            return False

        governance = data.get("governance", {})
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

    def _find_markdown_pair(self, json_path: Path) -> str:
        markdown_path = json_path.with_suffix(".md")
        if markdown_path.exists():
            return str(markdown_path)
        return ""

    def build_index(self, recent_limit: int = 5) -> Dict[str, Any]:
        packages: List[Dict[str, Any]] = []

        for path in sorted(self.packages_dir.glob("*.json")):
            if path.name == self.INDEX_FILE_NAME:
                continue

            data = self._load_json(path)
            if not data:
                continue

            if not self._is_campaign_package(data):
                continue

            packages.append(
                {
                    "file_name": path.name,
                    "json_path": str(path),
                    "markdown_path": self._find_markdown_pair(path),
                    "package_name": data.get("package_name", "pacote sem nome"),
                    "owner": data.get("owner", "nao informado"),
                    "generated_at": data.get("generated_at", ""),
                    "total_assets": int(data.get("total_assets", 0)),
                    "human_review_required": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "requires_final_approval": True,
                }
            )

        packages = sorted(
            packages,
            key=lambda item: item.get("generated_at", ""),
            reverse=True,
        )

        latest_package = packages[0] if packages else {}

        index = {
            "system": "K-Social Campaign Package Index",
            "generated_at": self._now(),
            "packages_dir": str(self.packages_dir),
            "total_packages": len(packages),
            "latest_package": latest_package,
            "recent_packages": packages[:recent_limit],
            "all_packages": packages,
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "requires_final_approval": True,
            },
        }

        return index

    def save_index(self, recent_limit: int = 5) -> Dict[str, Any]:
        index = self.build_index(recent_limit=recent_limit)

        self.index_file.write_text(
            json.dumps(index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return index


def main() -> None:
    indexer = SocialCampaignPackageIndexer()
    index = indexer.save_index()

    print("K-Social campaign package index generated.")
    print("Index file:", indexer.index_file)
    print("Total packages:", index["total_packages"])
    print("Recent packages:", len(index["recent_packages"]))
    print("Latest package:", index.get("latest_package", {}).get("package_name", "none"))
    print("Auto publish:", index["governance"]["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
