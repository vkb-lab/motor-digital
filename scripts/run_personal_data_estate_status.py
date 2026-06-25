from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_PERSONAL_DATA_ESTATE_REGISTRY.json"
SKILL = ROOT / "memory" / "kos_skills" / "KOS_SKILL_PERSONAL_DATA_ESTATE_GUARDIAN_V1.md"


def build_status() -> dict:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {
        "status": "KOS_PERSONAL_DATA_ESTATE_STATUS_READY",
        "registry_status": data.get("status"),
        "registry_exists": REGISTRY.exists(),
        "skill_exists": SKILL.exists(),
        "protected_domains_count": len(data.get("protected_domains", [])),
        "guardrails": data.get("guardrails", []),
        "external_api_accessed": False,
        "secrets_read": False,
    }


def main() -> None:
    print(json.dumps(build_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
