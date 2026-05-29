# -*- coding: utf-8 -*-
"""K-Social campaign package final approval queue.

Manages final human approval for exported campaign packages.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialCampaignPackageApprovalQueue:
    """Builds and updates final approval queue for campaign packages."""

    INDEX_FILE_NAME = "campaign_package_index.json"

    VALID_DECISIONS = {
        "pending_final_review",
        "approved_for_manual_use",
        "needs_package_revision",
        "rejected",
    }

    def __init__(
        self,
        packages_dir: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.packages_dir = (
            Path(packages_dir)
            if packages_dir
            else base_dir / "reports" / "campaign_packages"
        )
        self.memory_dir = (
            Path(memory_dir)
            if memory_dir
            else base_dir / "memory"
        )
        self.queue_file = self.memory_dir / "campaign_package_approval_queue.json"

        self.packages_dir.mkdir(parents=True, exist_ok=True)
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
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

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

    def _package_files(self) -> List[Path]:
        files: List[Path] = []

        for path in sorted(self.packages_dir.glob("*.json")):
            if path.name == self.INDEX_FILE_NAME:
                continue

            package = self._load_json(path)
            if not package:
                continue

            if self._is_valid_package(package):
                files.append(path)

        return files

    def _get_status(self, package: Dict[str, Any]) -> str:
        metadata = package.get("package_metadata", {})
        if not isinstance(metadata, dict):
            return "pending_final_review"

        status = metadata.get("final_approval_status", "pending_final_review")
        if status not in self.VALID_DECISIONS:
            return "pending_final_review"

        return status

    def _build_item(self, path: Path, package: Dict[str, Any]) -> Dict[str, Any]:
        governance = package.get("governance", {})

        return {
            "source_file": path.name,
            "package_name": package.get("package_name", "pacote sem nome"),
            "owner": package.get("owner", "nao informado"),
            "generated_at": package.get("generated_at", ""),
            "total_assets": int(package.get("total_assets", 0)),
            "final_approval_status": self._get_status(package),
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "requires_final_approval": bool(governance.get("requires_final_approval", True)),
        }

    def build_queue(self) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        for path in self._package_files():
            package = self._load_json(path)
            if not package:
                continue

            items.append(self._build_item(path, package))

        counts = {
            "pending_final_review": 0,
            "approved_for_manual_use": 0,
            "needs_package_revision": 0,
            "rejected": 0,
        }

        for item in items:
            status = item.get("final_approval_status", "pending_final_review")
            if status in counts:
                counts[status] += 1

        return {
            "system": "K-Social Campaign Package Approval Queue",
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
            raise ValueError("Invalid final approval decision.")

        if decision == "approved_for_auto_publish":
            raise ValueError("Auto-publish approval is blocked.")

        package_path = self.packages_dir / source_file

        if not package_path.exists():
            raise FileNotFoundError(f"Package file not found: {source_file}")

        package = self._load_json(package_path)

        if not package or not self._is_valid_package(package):
            raise ValueError("Invalid campaign package.")

        metadata = package.get("package_metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        metadata["final_approval_status"] = decision
        metadata["last_reviewed_at"] = self._now()
        metadata["last_reviewer"] = reviewer
        metadata["last_review_notes"] = notes

        package["package_metadata"] = metadata

        events = package.get("final_approval_events", [])
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

        package["final_approval_events"] = events

        governance = package.get("governance", {})
        if not isinstance(governance, dict):
            governance = {}

        governance["human_review_required"] = True
        governance["publication_permission"] = False
        governance["external_api_used"] = False
        governance["approved_for_auto_publish"] = False
        governance["requires_final_approval"] = True

        package["governance"] = governance

        self._save_json(package_path, package)
        return self.save_queue()


def main() -> None:
    queue_manager = SocialCampaignPackageApprovalQueue()
    queue = queue_manager.save_queue()

    print("K-Social campaign package approval queue generated.")
    print("Queue file:", queue_manager.queue_file)
    print("Total items:", queue["total_items"])
    print("Pending final review:", queue["counts"]["pending_final_review"])
    print("Approved for manual use:", queue["counts"]["approved_for_manual_use"])
    print("Needs package revision:", queue["counts"]["needs_package_revision"])
    print("Rejected:", queue["counts"]["rejected"])
    print("Auto publish:", queue["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
