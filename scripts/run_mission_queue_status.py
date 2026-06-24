from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "local_runtime" / "kos_mission_queue_status"
LATEST = OUT_DIR / "latest_mission_queue_status.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def main() -> int:
    paths = {
        "latest_queue_processor_status": ROOT / "local_runtime" / "kos_autonomy_missions" / "latest_queue_processor_status.json",
        "latest_mission_queue_loop_tick": ROOT / "local_runtime" / "kos_autonomy_missions" / "latest_mission_queue_loop_tick.json",
        "human_decision_queue": ROOT / "live" / "human_decision_center" / "decision_queue.json",
        "latest_action_packet": ROOT / "local_runtime" / "kos_action_router" / "latest_action_packet.json",
        "latest_safe_action": ROOT / "local_runtime" / "kos_safe_actions" / "latest_safe_action.json",
    }
    payload = {
        "status": "KOS_MISSION_QUEUE_STATUS_READY",
        "created_at": now_iso(),
        "sources": {key: read_json(path) for key, path in paths.items()},
        "read_only": True,
        "real_action_executed": False,
        "external_side_effects_executed": False,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
