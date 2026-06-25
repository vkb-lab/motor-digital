from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_LOCAL_STORAGE_ESTATE_REGISTRY.json"


def build_status() -> dict:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    allowed_roots = data.get("allowed_roots", [])
    roots = [
        {"path": item, "exists": (ROOT / item).exists()}
        for item in allowed_roots
    ]
    return {
        "status": "KOS_LOCAL_STORAGE_ESTATE_STATUS_READY",
        "registry_status": data.get("status"),
        "scope": data.get("scope"),
        "allowed_roots": roots,
        "forbidden_behaviors": data.get("forbidden_behaviors", []),
        "full_disk_scan_performed": False,
        "mass_hashing_performed": False,
        "external_api_accessed": False,
    }


def main() -> None:
    print(json.dumps(build_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
