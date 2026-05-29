from __future__ import annotations

import json
from pathlib import Path

from .brief import build_default_k_atlas_brief
from .package_builder import build_creative_media_package


def export_default_k_atlas_creative_package(
    output_path: str = "reports/creative_media/k_atlas_creative_media_package.json",
) -> dict:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    brief = build_default_k_atlas_brief()
    package = build_creative_media_package(brief)

    report = {
        "checkpoint": "32",
        "name": "Creative Media Gateway",
        "package": package,
    }

    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(export_default_k_atlas_creative_package(), ensure_ascii=False, indent=2))