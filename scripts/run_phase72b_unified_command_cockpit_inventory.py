from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local_runtime" / "kos_unified_cockpit" / "latest_inventory.json"

CATEGORIES = {
    "runtime": ["runtime", "scheduler", "supervisor", "health", "startup"],
    "agents": ["agent", "autonomy", "planner", "mission", "queue", "handoff", "coworker"],
    "bridge": ["chatgpt", "engineer", "command", "intake", "promotion"],
    "products_saas": ["product", "saas", "factory", "scaffold", "export", "registry"],
    "social_publish": ["social", "publish", "instagram", "hupmix", "readiness", "ledger"],
    "patches": ["patch", "proposal", "review"],
    "dashboards": ["dashboard", "cockpit", "launcher", "panel", "workspace"],
}

SAFE_FLAGS = {
    "auto_publish_enabled": False,
    "auto_execution_enabled": False,
    "operator_review_required": True,
    "parada_atlantida_locked": True,
    "paid_ai_locked": True,
    "browser_scraping_enabled": False,
    "instagram_publish_executed": False,
    "real_action_executed": False,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def list_files(folder: str) -> list[str]:
    base = ROOT / folder
    if not base.exists():
        return []
    return sorted(rel(p) for p in base.rglob("*") if p.is_file())


def match_category(files: list[str], keywords: list[str]) -> list[str]:
    result = []
    for item in files:
        low = item.lower()
        if any(k.lower() in low for k in keywords):
            result.append(item)
    return sorted(result)


def build_inventory() -> dict[str, Any]:
    files = []
    for folder in ["pages", "scripts", "config", "reports", "docs", "tests"]:
        files.extend(list_files(folder))

    grouped = {
        name: match_category(files, keywords)
        for name, keywords in CATEGORIES.items()
    }

    key_reports = {
        "70_1_chatgpt_bridge_baseline": (ROOT / "reports/KOS_PHASE701_CHATGPT_LOCAL_BRIDGE_BASELINE_CERTIFICATION.json").exists(),
        "71a_social_ops": (ROOT / "reports/KOS_PHASE71A_SOCIAL_OPS_CONTROL_CENTER_BOOTSTRAP.json").exists(),
        "71b_social_strategy": (ROOT / "reports/KOS_PHASE71B_SOCIAL_STRATEGY_GENERATOR_BOOTSTRAP.json").exists(),
        "71c_publish_readiness": (ROOT / "reports/KOS_PHASE71C_SOCIAL_PUBLISH_READINESS_AUDITOR_BOOTSTRAP.json").exists(),
        "72a_weekly_workspace": (ROOT / "reports/KOS_PHASE72A_WEEKLY_OPERATOR_WORKSPACE_BOOTSTRAP.json").exists(),
    }

    inventory = {
        "status": "KOS_UNIFIED_COMMAND_COCKPIT_INVENTORY_READY",
        "phase": "72B",
        "total_files_indexed": len(files),
        "categories": grouped,
        "counts": {name: len(items) for name, items in grouped.items()},
        "key_reports": key_reports,
        "safe_flags": SAFE_FLAGS,
        "created_at": now_iso(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    return inventory


def main() -> int:
    print(json.dumps(build_inventory(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
