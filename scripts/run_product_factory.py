from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "local_runtime" / "kos_product_factory"
LATEST = OUT_DIR / "latest_product_factory_alias.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="draft")
    parser.add_argument("--idea", default="Produto SaaS local gerado pelo K-OS")
    parser.add_argument("--target-user", default="pequenos negocios")
    parser.add_argument("--market", default="operacao local com IA supervisionada")
    args = parser.parse_args()

    mission = {}
    status = "KOS_PRODUCT_FACTORY_ALIAS_READY"
    error = ""

    try:
        from k_atlas.product_factory.mission_layer import (
            create_product_mission,
            export_to_kaizen_mission_dry_run,
            summarize_product_missions,
        )

        mission = create_product_mission(
            idea=args.idea,
            product_type="saas",
            target_user=args.target_user,
            market=args.market,
            priority="medium",
            source="run_product_factory_alias",
        )
        summary = summarize_product_missions(limit=10)
        export = export_to_kaizen_mission_dry_run(mission)
    except Exception as exc:
        status = "KOS_PRODUCT_FACTORY_ALIAS_ATTENTION_REQUIRED"
        error = str(exc)
        summary = {}
        export = {}

    payload = {
        "status": status,
        "created_at": now_iso(),
        "mode": args.mode,
        "idea": args.idea,
        "mission_id": mission.get("mission_id"),
        "title": mission.get("title"),
        "product_type": mission.get("product_type", "saas"),
        "tasks_count": len(mission.get("tasks", []) or []),
        "summary": summary,
        "export_dry_run": export,
        "error": error,
        "real_action_executed": False,
        "external_side_effects_executed": False,
        "paid_ai_call_executed": False,
        "deploy_executed": False,
    }
    write_json(LATEST, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "KOS_PRODUCT_FACTORY_ALIAS_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
