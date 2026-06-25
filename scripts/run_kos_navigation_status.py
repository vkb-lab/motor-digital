from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_CUSTOM_NAVIGATION_REGISTRY.json"


def build_status() -> dict:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    core = data.get("official_core", [])
    return {
        "status": "KOS_CUSTOM_NAVIGATION_STATUS_READY",
        "registry_status": data.get("status"),
        "official_core_found": [path for path in core if (ROOT / path).exists()],
        "official_core_missing": [path for path in core if not (ROOT / path).exists()],
        "legacy_groups_to_hide": data.get("legacy_groups_to_hide", []),
        "pages_moved": False,
        "pages_removed": False,
        "app_py_changed_by_this_step": False,
    }


def main() -> None:
    print(json.dumps(build_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
