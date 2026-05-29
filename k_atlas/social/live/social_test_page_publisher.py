# -*- coding: utf-8 -*-
"""K-Social local test page publisher.

Builds and validates local test-page payloads from a manually approved campaign package.
It does not publish to real social networks, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialTestPagePublisher:
    """Creates dry-run payloads for a local test page."""

    def __init__(
        self,
        social_dir: Optional[Path] = None,
    ) -> None:
        self.social_dir = Path(social_dir) if social_dir else Path(__file__).resolve().parents[1]
        self.memory_dir = self.social_dir / "memory"
        self.reports_dir = self.social_dir / "reports"
        self.packages_dir = self.reports_dir / "campaign_packages"
        self.plan_dir = self.reports_dir / "test_page_publish_plan"
        self.receipts_dir = self.reports_dir / "test_page_publish_receipts"

        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.plan_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.memory_dir / "test_page_config.json"
        self.latest_campaign_file = self.packages_dir / "latest_manual_approved_campaign.json"

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

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def ensure_test_page_config(self) -> Dict[str, Any]:
        """Create or load local test-page config."""

        if self.config_file.exists():
            config = self._load_json(self.config_file)
            if config:
                return config

        config = {
            "system": "K-Social Local Test Page Config",
            "created_at": self._now(),
            "page_name": "K-Social Test Page",
            "page_id": "local-test-page",
            "environment": "local_dry_run",
            "real_api_enabled": False,
            "browser_automation_enabled": False,
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "human_review_required": True,
            "allowed_channels": [
                "Instagram Test",
                "Facebook Test",
                "WhatsApp Test",
                "Google Business Profile Test"
            ],
            "notes": [
                "This is a local dry-run page adapter.",
                "No content is published to real social networks.",
                "Use this only to validate payloads, approvals and reports."
            ],
        }

        self._save_json(self.config_file, config)
        return config

    def load_latest_campaign_pointer(self) -> Dict[str, Any]:
        """Load latest manually approved campaign pointer."""

        data = self._load_json(self.latest_campaign_file)

        if not data.get("latest_found", False):
            raise RuntimeError("Nenhuma campanha principal aprovada foi encontrada.")

        campaign = data.get("campaign", {})
        governance = data.get("governance", {})

        if campaign.get("approval_status") != "approved_for_manual_use":
            raise RuntimeError("Campanha principal ainda nao esta aprovada para uso manual.")

        if governance.get("publication_permission") is not False:
            raise RuntimeError("Permissao de publicacao deve permanecer bloqueada.")

        if governance.get("approved_for_auto_publish") is not False:
            raise RuntimeError("Auto publish deve permanecer bloqueado.")

        return data

    def load_campaign_package(self, pointer: Dict[str, Any]) -> Dict[str, Any]:
        """Load the campaign package referenced by the latest pointer."""

        campaign = pointer.get("campaign", {})
        json_path = Path(str(campaign.get("json_path", "")))

        if not json_path.exists():
            raise FileNotFoundError(f"Pacote aprovado nao encontrado: {json_path}")

        package = self._load_json(json_path)

        if package.get("system") != "K-Social Campaign Package Exporter":
            raise RuntimeError("Pacote aprovado invalido.")

        governance = package.get("governance", {})

        if governance.get("publication_permission") is not False:
            raise RuntimeError("Pacote nao pode ter permissao de publicacao.")

        if governance.get("approved_for_auto_publish") is not False:
            raise RuntimeError("Pacote nao pode aprovar auto publish.")

        return package

    def _asset_kind(self, file_name: str) -> str:
        name = file_name.lower()

        if "caption" in name:
            return "caption"
        if "hook" in name:
            return "hook_variations"
        if "reel" in name:
            return "reel_script"
        if "image" in name:
            return "ai_image_prompt"
        if "video" in name:
            return "ai_video_prompt"

        return "creative_asset"

    def build_test_plan(self, package: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build dry-run payload plan for local test page."""

        assets = package.get("assets", [])
        if not isinstance(assets, list):
            assets = []

        items: List[Dict[str, Any]] = []

        for index, asset in enumerate(assets, start=1):
            file_name = str(asset.get("file_name", f"asset_{index}.md"))
            content = str(asset.get("content", ""))

            items.append(
                {
                    "item_id": f"test_payload_{index:02d}",
                    "asset_file": file_name,
                    "asset_path": str(asset.get("path", "")),
                    "asset_kind": self._asset_kind(file_name),
                    "target_page": config.get("page_name", "K-Social Test Page"),
                    "target_environment": config.get("environment", "local_dry_run"),
                    "channels": config.get("allowed_channels", []),
                    "content_preview": content[:1200],
                    "status": "ready_for_local_test",
                    "real_publish": False,
                    "dry_run": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "human_review_required": True,
                }
            )

        plan = {
            "system": "K-Social Test Page Publish Plan",
            "generated_at": self._now(),
            "package_name": package.get("package_name", "pacote sem nome"),
            "product_filter": package.get("product_filter", ""),
            "target_page": config.get("page_name", "K-Social Test Page"),
            "environment": config.get("environment", "local_dry_run"),
            "total_payloads": len(items),
            "items": items,
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "real_publish": False,
                "dry_run": True,
            },
        }

        return plan

    def save_plan(self, plan: Dict[str, Any]) -> Path:
        path = self.plan_dir / "latest_test_page_publish_plan.json"
        self._save_json(path, plan)

        md_path = self.plan_dir / "latest_test_page_publish_plan.md"

        lines: List[str] = []
        lines.append("# K-Social Test Page Publish Plan")
        lines.append("")
        lines.append(f"Generated at: {plan['generated_at']}")
        lines.append(f"Package: {plan['package_name']}")
        lines.append(f"Target page: {plan['target_page']}")
        lines.append(f"Environment: {plan['environment']}")
        lines.append("")
        lines.append("## Governance")
        lines.append("")
        lines.append("- Real publish: False")
        lines.append("- Dry run: True")
        lines.append("- Publication permission: False")
        lines.append("- External API used: False")
        lines.append("- Approved for auto publish: False")
        lines.append("- Human review required: True")
        lines.append("")
        lines.append("## Payloads")
        lines.append("")

        for item in plan["items"]:
            lines.append(f"### {item['item_id']} - {item['asset_kind']}")
            lines.append("")
            lines.append(f"- Asset: {item['asset_file']}")
            lines.append(f"- Status: {item['status']}")
            lines.append(f"- Real publish: {item['real_publish']}")
            lines.append("")
            lines.append("```text")
            lines.append(item["content_preview"])
            lines.append("```")
            lines.append("")

        md_path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def simulate_local_test_page(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate local test-page execution and generate receipts."""

        receipts: List[Dict[str, Any]] = []

        for item in plan.get("items", []):
            receipts.append(
                {
                    "item_id": item.get("item_id", ""),
                    "asset_file": item.get("asset_file", ""),
                    "asset_kind": item.get("asset_kind", ""),
                    "target_page": item.get("target_page", ""),
                    "status": "validated_in_local_test_page",
                    "real_publish": False,
                    "dry_run": True,
                    "publication_permission": False,
                    "external_api_used": False,
                    "approved_for_auto_publish": False,
                    "validated_at": self._now(),
                }
            )

        result = {
            "system": "K-Social Local Test Page Receipts",
            "generated_at": self._now(),
            "target_page": plan.get("target_page", "K-Social Test Page"),
            "package_name": plan.get("package_name", ""),
            "payloads_received": len(plan.get("items", [])),
            "payloads_validated": len(receipts),
            "receipts": receipts,
            "governance": {
                "real_publish": False,
                "dry_run": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "human_review_required": True,
            },
        }

        receipts_path = self.receipts_dir / "latest_test_page_receipts.json"
        self._save_json(receipts_path, result)

        return result

    def run(self) -> Dict[str, Any]:
        """Run complete local test-page validation."""

        config = self.ensure_test_page_config()
        pointer = self.load_latest_campaign_pointer()
        package = self.load_campaign_package(pointer)
        plan = self.build_test_plan(package=package, config=config)
        plan_path = self.save_plan(plan)
        receipts = self.simulate_local_test_page(plan)

        return {
            "system": "K-Social Test Page Publisher",
            "generated_at": self._now(),
            "config_file": str(self.config_file),
            "plan_file": str(plan_path),
            "package_name": plan.get("package_name", ""),
            "payloads_planned": plan.get("total_payloads", 0),
            "payloads_validated": receipts.get("payloads_validated", 0),
            "publication_permission": False,
            "external_api_used": False,
            "approved_for_auto_publish": False,
            "human_review_required": True,
            "dry_run": True,
        }


def main() -> None:
    publisher = SocialTestPagePublisher()
    result = publisher.run()

    print("K-Social local test page validation completed.")
    print("Package:", result["package_name"])
    print("Payloads planned:", result["payloads_planned"])
    print("Payloads validated:", result["payloads_validated"])
    print("Dry run:", result["dry_run"])
    print("Publication permission:", result["publication_permission"])
    print("Auto publish:", result["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
