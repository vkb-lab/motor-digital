from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "memory" / "kos_governance" / "KOS_ORIGIN_CORE_REGISTRY.json"


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8-sig"))


def relative_exists(path_text: str) -> bool:
    return (ROOT / path_text).exists()


def build_status() -> dict[str, Any]:
    registry = load_registry()
    core_files = registry.get("priority_core_files", [])
    found = [path for path in core_files if relative_exists(path)]
    missing = [path for path in core_files if not relative_exists(path)]

    return {
        "status": "KOS_ORIGIN_CORE_STATUS_READY",
        "registry_status": registry.get("status"),
        "essence": registry.get("essence"),
        "official_home": registry.get("official_home"),
        "official_home_exists": relative_exists(str(registry.get("official_home", ""))),
        "cloud_readonly": registry.get("cloud_readonly"),
        "cloud_readonly_exists": relative_exists(str(registry.get("cloud_readonly", ""))),
        "core_files_found": found,
        "core_files_missing": missing,
        "core_files_found_count": len(found),
        "core_files_missing_count": len(missing),
        "legacy_warning": {
            "hide_from_primary_navigation": registry.get("legacy_to_hide", []),
            "do_not_delete": True,
        },
        "external_tools_role": registry.get("external_tools_role"),
        "private_doctrine": registry.get("private_doctrine"),
        "next_patch_recommended": registry.get("next_patch_recommended"),
        "guardrails": {
            "external_api_accessed": False,
            "secrets_read": False,
            "runtime_local_read": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="K-OS Origin Core Registry status")
    parser.add_argument("--mode", choices=["status"], default="status")
    parser.parse_args()
    print(json.dumps(build_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
