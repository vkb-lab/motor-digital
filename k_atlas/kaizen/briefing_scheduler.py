from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "briefing_scheduler"
LAST_TICK = LOG_DIR / "last_briefing_scheduler_tick.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def run_briefing_scheduler_tick(cycle_id: str = "briefing_scheduler_tick") -> dict:
    try:
        from k_atlas.kaizen.scheduler_gate import run_scheduler_tick
        scheduler_result = run_scheduler_tick(cycle_id=cycle_id)
    except Exception as exc:
        scheduler_result = {
            "status": "SCHEDULER_TICK_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    try:
        from k_atlas.kaizen.operator_briefing import build_operator_briefing
        briefing = build_operator_briefing(write_log=True)
    except Exception as exc:
        briefing = {
            "status": "OPERATOR_BRIEFING_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    report = {
        "status": "BRIEFING_SCHEDULER_TICK_COMPLETED",
        "cycle_id": cycle_id,
        "scheduler_result": scheduler_result,
        "operator_briefing": {
            "status": briefing.get("status"),
            "risk_level": briefing.get("risk_level"),
            "health_status": briefing.get("health_status"),
            "priorities": briefing.get("priorities", []),
            "summary": briefing.get("summary", {}),
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    _save_json(LAST_TICK, report)
    return report

def summarize_briefing_scheduler() -> dict:
    if LAST_TICK.exists():
        try:
            last_tick = json.loads(LAST_TICK.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            last_tick = {"error": str(exc)}
    else:
        last_tick = {}

    return {
        "status": "BRIEFING_SCHEDULER_SUMMARY",
        "last_tick_exists": LAST_TICK.exists(),
        "last_tick_path": str(LAST_TICK.relative_to(ROOT)).replace("\\", "/"),
        "last_tick": last_tick,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }

if __name__ == "__main__":
    print(json.dumps(run_briefing_scheduler_tick("phase47_smoke"), ensure_ascii=False, indent=2))
