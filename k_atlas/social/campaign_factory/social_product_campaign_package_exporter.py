# -*- coding: utf-8 -*-
"""K-Social product-specific campaign package exporter.

Exports a supervised campaign package filtered by product/campaign name.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialProductCampaignPackageExporter:
    """Exports a product-specific campaign package from refinement outputs."""

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

    def _normalize(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

    def load_refinement_outputs(self, product_filter: str) -> List[Dict[str, str]]:
        """Load only refinement outputs related to a product."""

        outputs: List[Dict[str, str]] = []
        normalized_filter = self._normalize(product_filter)

        for path in sorted(self.refinement_outputs_dir.glob("*.md")):
            try:
                content = path.read_text(encoding="utf-8-sig")
            except OSError:
                continue

            searchable = self._normalize(path.name + " " + content)

            if normalized_filter not in searchable:
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
        package_name: str,
        product_filter: str,
        owner: str = "K-Atlas Operator",
    ) -> Dict[str, Any]:
        """Build product-specific package."""

        assets = self.load_refinement_outputs(product_filter=product_filter)

        return {
            "system": "K-Social Campaign Package Exporter",
            "package_name": package_name,
            "product_filter": product_filter,
            "owner": owner,
            "generated_at": self._now(),
            "source_outputs_dir": str(self.refinement_outputs_dir),
            "total_assets": len(assets),
            "assets": assets,
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "requires_final_approval": True,
                "manual_use_only": True,
            },
            "brand_safety_notes": [
                "Campanha tematica de futebol, nao oficial.",
                "Nao usar logos oficiais.",
                "Nao afirmar patrocinio oficial.",
                "Nao prometer transmissao sem validar direitos.",
                "Revisao humana obrigatoria antes de qualquer uso real."
            ],
            "next_steps": [
                "Revisar todos os assets manualmente.",
                "Escolher as melhores legendas e roteiros.",
                "Ajustar linguagem local para Parada Atlantida e Chopp Ecobier.",
                "Enviar para aprovacao final manual.",
                "Manter publicacao automatica bloqueada."
            ],
        }

    def save_package(self, package: Dict[str, Any]) -> Dict[str, str]:
        """Save package as JSON and Markdown."""

        slug = self._slugify(str(package.get("package_name", "campaign-package")))
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        json_path = self.output_dir / f"{slug}_{timestamp}.json"
        md_path = self.output_dir / f"{slug}_{timestamp}.md"

        json_path.write_text(
            json.dumps(package, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        lines: List[str] = []

        lines.append("# K-Social Campaign Package")
        lines.append("")
        lines.append(f"Package name: {package['package_name']}")
        lines.append(f"Product filter: {package['product_filter']}")
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
        lines.append(f"- Manual use only: {governance['manual_use_only']}")
        lines.append("")
        lines.append("## Brand Safety")
        lines.append("")

        for note in package["brand_safety_notes"]:
            lines.append(f"- {note}")

        lines.append("")
        lines.append("## Assets")
        lines.append("")

        if not package["assets"]:
            lines.append("- No matching refinement assets found.")
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
        package_name: str,
        product_filter: str,
        owner: str = "K-Atlas Operator",
    ) -> Dict[str, Any]:
        """Build and save product-specific package."""

        package = self.build_package(
            package_name=package_name,
            product_filter=product_filter,
            owner=owner,
        )
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
    parser = argparse.ArgumentParser(description="Export product-specific K-Social campaign package.")
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--product-filter", required=True)
    parser.add_argument("--owner", default="K-Atlas Operator")

    args = parser.parse_args()

    exporter = SocialProductCampaignPackageExporter()
    result = exporter.run(
        package_name=args.package_name,
        product_filter=args.product_filter,
        owner=args.owner,
    )

    print("K-Social product campaign package exported.")
    print("Package:", result["package"]["package_name"])
    print("Product filter:", result["package"]["product_filter"])
    print("Assets:", result["package"]["total_assets"])
    print("JSON:", result["paths"]["json_path"])
    print("Markdown:", result["paths"]["markdown_path"])
    print("Publication permission:", result["publication_permission"])
    print("Auto publish:", result["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
