# -*- coding: utf-8 -*-
"""K-Social campaign package exporter.

Builds a supervised local campaign package from refined creative outputs.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialCampaignPackageExporter:
    """Exports campaign packages from refinement outputs."""

    def __init__(
        self,
        refinement_outputs_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.refinement_outputs_dir = (
            Path(refinement_outputs_dir)
            if refinement_outputs_dir
            else base_dir / "reports" / "refinement_outputs"
        )
        self.output_dir = (
            Path(output_dir)
            if output_dir
            else base_dir / "reports" / "campaign_packages"
        )
        self.refinement_outputs_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = value.strip("-")
        return value or "campaign-package"

    def load_refinement_outputs(self) -> List[Dict[str, str]]:
        """Load generated Markdown refinement outputs."""

        outputs: List[Dict[str, str]] = []

        for path in sorted(self.refinement_outputs_dir.glob("*.md")):
            try:
                content = path.read_text(encoding="utf-8-sig")
            except OSError:
                continue

            outputs.append(
                {
                    "file_name": path.name,
                    "path": str(path),
                    "content": content,
                }
            )

        return outputs

    def build_package(
        self,
        package_name: str = "K-Social Campaign Package",
        owner: str = "K-Atlas Operator",
    ) -> Dict[str, Any]:
        """Build campaign package from refinement outputs."""

        outputs = self.load_refinement_outputs()

        return {
            "system": "K-Social Campaign Package Exporter",
            "package_name": package_name,
            "owner": owner,
            "generated_at": self._now(),
            "source_outputs_dir": str(self.refinement_outputs_dir),
            "total_assets": len(outputs),
            "assets": outputs,
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "requires_final_approval": True,
            },
            "next_steps": [
                "Review all creative assets manually.",
                "Check legal and brand safety before any real campaign.",
                "Select approved assets for future scheduling module.",
                "Keep auto-publishing disabled.",
            ],
        }

    def save_package(self, package: Dict[str, Any]) -> Dict[str, str]:
        """Save campaign package as JSON and Markdown."""

        package_slug = self._slugify(str(package.get("package_name", "campaign-package")))
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        json_path = self.output_dir / f"{package_slug}_{timestamp}.json"
        md_path = self.output_dir / f"{package_slug}_{timestamp}.md"

        json_path.write_text(
            json.dumps(package, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        lines: List[str] = []

        lines.append("# K-Social Campaign Package")
        lines.append("")
        lines.append(f"Package name: {package['package_name']}")
        lines.append(f"Owner: {package['owner']}")
        lines.append(f"Generated at: {package['generated_at']}")
        lines.append("")
        lines.append("## Governance")
        lines.append("")
        governance = package["governance"]
        lines.append(f"- Human review required: {governance['human_review_required']}")
        lines.append(f"- Publication permission: {governance['publication_permission']}")
        lines.append(f"- External API used: {governance['external_api_used']}")
        lines.append(f"- Approved for auto publish: {governance['approved_for_auto_publish']}")
        lines.append(f"- Requires final approval: {governance['requires_final_approval']}")
        lines.append("")
        lines.append("## Assets")
        lines.append("")

        if not package["assets"]:
            lines.append("- No refinement assets found.")
        else:
            for asset in package["assets"]:
                lines.append(f"### {asset['file_name']}")
                lines.append("")
                lines.append(asset["content"])
                lines.append("")

        lines.append("## Next Steps")
        lines.append("")

        for step in package["next_steps"]:
            lines.append(f"- {step}")

        lines.append("")

        md_path.write_text("\n".join(lines), encoding="utf-8")

        return {
            "json_path": str(json_path),
            "markdown_path": str(md_path),
        }

    def run(
        self,
        package_name: str = "K-Social Campaign Package",
        owner: str = "K-Atlas Operator",
    ) -> Dict[str, Any]:
        """Build and save package."""

        package = self.build_package(package_name=package_name, owner=owner)
        paths = self.save_package(package)

        return {
            "package": package,
            "paths": paths,
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "approved_for_auto_publish": False,
        }


def main() -> None:
    exporter = SocialCampaignPackageExporter()
    result = exporter.run(
        package_name="BRICS Paraguay Autos Campaign Package",
        owner="K-Atlas Operator",
    )

    package = result["package"]

    print("K-Social campaign package exported.")
    print("Assets:", package["total_assets"])
    print("JSON:", result["paths"]["json_path"])
    print("Markdown:", result["paths"]["markdown_path"])
    print("Publication permission:", result["publication_permission"])
    print("Approved for auto publish:", result["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
