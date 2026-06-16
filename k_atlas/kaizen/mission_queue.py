from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "local_runtime" / "kaizen" / "mission_queue.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "missions"
POLICY_PATH = ROOT / "config" / "kos_mission_queue_policy.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Mission:
    id: str
    title: str
    description: str
    priority: str = "medium"
    status: str = "draft"
    approval_status: str = "not_requested"
    execution_allowed: bool = False
    created_at: str = ""
    updated_at: str = ""

def _load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _event(event: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event["created_at"] = now()
    path = LOG_DIR / "events.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def load_queue() -> dict:
    return _load_json(QUEUE_PATH, {
        "status": "READY",
        "missions": [],
        "created_at": now(),
        "updated_at": now()
    })

def save_queue(queue: dict) -> dict:
    queue["updated_at"] = now()
    _save_json(QUEUE_PATH, queue)
    return queue

def create_mission(title: str, description: str, priority: str = "medium") -> dict:
    queue = load_queue()

    mission = Mission(
        id="KOS-MISSION-" + uuid.uuid4().hex[:10].upper(),
        title=title.strip(),
        description=description.strip(),
        priority=priority.strip() or "medium",
        status="draft",
        approval_status="not_requested",
        execution_allowed=False,
        created_at=now(),
        updated_at=now()
    )

    queue.setdefault("missions", []).append(asdict(mission))
    save_queue(queue)

    _event({
        "event": "mission_created",
        "mission_id": mission.id,
        "title": mission.title,
        "execution_allowed": False
    })

    return asdict(mission)

def plan_mission(mission_id: str) -> dict:
    queue = load_queue()
    mission = None

    for item in queue.get("missions", []):
        if item.get("id") == mission_id:
            mission = item
            break

    if not mission:
        return {
            "ok": False,
            "status": "MISSION_NOT_FOUND",
            "mission_id": mission_id
        }

    try:
        from k_atlas.kaizen.planner_bridge import run_planner_bridge
        plan = run_planner_bridge(
            mission=mission.get("description", ""),
            mission_id=mission_id
        )
    except Exception as exc:
        plan = {
            "status": "PLANNER_BRIDGE_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    mission["status"] = "planned"
    mission["approval_status"] = "pending_human_review"
    mission["execution_allowed"] = False
    mission["updated_at"] = now()
    mission["last_plan"] = plan

    save_queue(queue)

    _event({
        "event": "mission_planned",
        "mission_id": mission_id,
        "execution_allowed": False,
        "planner_status": plan.get("status")
    })

    return {
        "ok": True,
        "status": "MISSION_PLANNED",
        "mission": mission,
        "plan": plan,
        "execution_allowed": False
    }

def approve_mission(mission_id: str, typed_confirmation: str) -> dict:
    queue = load_queue()
    required = "YES_APPROVE_DRY_RUN_ONLY"

    mission = None
    for item in queue.get("missions", []):
        if item.get("id") == mission_id:
            mission = item
            break

    if not mission:
        return {
            "ok": False,
            "status": "MISSION_NOT_FOUND",
            "mission_id": mission_id
        }

    if typed_confirmation.strip().upper() != required:
        return {
            "ok": False,
            "status": "APPROVAL_REJECTED",
            "reason": "confirmacao incorreta",
            "required": required,
            "execution_allowed": False
        }

    mission["approval_status"] = "approved_for_dry_run_only"
    mission["execution_allowed"] = False
    mission["status"] = "approved_dry_run"
    mission["updated_at"] = now()

    save_queue(queue)

    _event({
        "event": "mission_approved_dry_run_only",
        "mission_id": mission_id,
        "execution_allowed": False
    })

    return {
        "ok": True,
        "status": "MISSION_APPROVED_DRY_RUN_ONLY",
        "mission": mission,
        "execution_allowed": False
    }

def summarize_queue() -> dict:
    queue = load_queue()
    missions = queue.get("missions", [])
    return {
        "status": queue.get("status", "READY"),
        "total": len(missions),
        "draft": len([m for m in missions if m.get("status") == "draft"]),
        "planned": len([m for m in missions if m.get("status") == "planned"]),
        "approved_dry_run": len([m for m in missions if m.get("status") == "approved_dry_run"]),
        "execution_allowed_count": len([m for m in missions if m.get("execution_allowed") is True]),
        "queue_path": str(QUEUE_PATH),
        "missions": missions
    }

if __name__ == "__main__":
    mission = create_mission(
        title="Demo Fase 37",
        description="Planejar proximo incremento seguro do K-OS sem executar alteracoes.",
        priority="high"
    )
    planned = plan_mission(mission["id"])
    print(json.dumps({
        "created": mission,
        "planned": planned,
        "summary": summarize_queue(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
