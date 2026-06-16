from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

from k_atlas.kaizen.mission_queue import create_mission, plan_mission
from k_atlas.kaizen.human_approval import (
    create_approval_request,
    approve_dry_run,
    DRY_RUN_CONFIRMATION,
)
from k_atlas.kaizen.safe_executor import run_safe_bundle

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "closed_loop"
POLICY_PATH = ROOT / "config" / "kos_closed_loop_policy.json"

DEFAULT_SAFE_ACTIONS = ["git_branch", "git_status"]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _event(event: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event["created_at"] = now()
    with (LOG_DIR / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def run_closed_loop(
    title: str,
    description: str,
    priority: str = "high",
    typed_confirmation: str = "",
    safe_actions: list[str] | None = None,
) -> dict:
    loop_id = "KOS-LOOP-" + uuid.uuid4().hex[:10].upper()
    safe_actions = safe_actions or DEFAULT_SAFE_ACTIONS

    _event({
        "event": "closed_loop_started",
        "loop_id": loop_id,
        "title": title,
        "safe_actions": safe_actions,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    })

    mission = create_mission(
        title=title,
        description=description,
        priority=priority,
    )

    plan = plan_mission(mission["id"])

    approval = create_approval_request(
        title=f"Aprovar dry-run do loop {loop_id}",
        description="Aprovar somente execucao sandbox allowlist. Nenhuma acao externa real.",
        action_type="closed_loop_safe_bundle",
        risk_level="low",
        payload={
            "loop_id": loop_id,
            "mission_id": mission["id"],
            "safe_actions": safe_actions,
        },
    )

    approval_result = None
    executor_result = None

    if typed_confirmation.strip().upper() == DRY_RUN_CONFIRMATION:
        approval_result = approve_dry_run(approval["id"], typed_confirmation)

        if approval_result.get("ok") is True:
            executor_result = run_safe_bundle(
                bundle_id=loop_id,
                actions=safe_actions,
                dry_run=False,
            )
    else:
        approval_result = {
            "ok": False,
            "status": "WAITING_FOR_HUMAN_APPROVAL",
            "required_confirmation": DRY_RUN_CONFIRMATION,
            "execution_allowed": False,
        }

    status = "CLOSED_LOOP_SANDBOX_COMPLETED" if executor_result else "CLOSED_LOOP_WAITING_APPROVAL"

    report = {
        "status": status,
        "loop_id": loop_id,
        "mission": mission,
        "plan": plan,
        "approval_request": approval,
        "approval_result": approval_result,
        "executor_result": executor_result,
        "safe_actions": safe_actions,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    report_path = LOG_DIR / f"{loop_id}.json"
    _save_json(report_path, report)

    _event({
        "event": "closed_loop_finished",
        "loop_id": loop_id,
        "status": status,
        "executor_ran": executor_result is not None,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    })

    return report

def summarize_last_reports(limit: int = 10) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    reports = sorted(LOG_DIR.glob("KOS-LOOP-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    items = []
    for path in reports[:limit]:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            items.append({
                "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "loop_id": data.get("loop_id"),
                "status": data.get("status"),
                "mission_id": data.get("mission", {}).get("id"),
                "executor_ran": data.get("executor_result") is not None,
                "real_action_executed": data.get("real_action_executed"),
                "paid_ai_call_executed": data.get("paid_ai_call_executed"),
                "instagram_publish_executed": data.get("instagram_publish_executed"),
                "created_at": data.get("created_at"),
            })
        except Exception:
            pass

    return {
        "status": "CLOSED_LOOP_REPORTS_SUMMARY",
        "count": len(items),
        "reports": items,
    }

if __name__ == "__main__":
    result = run_closed_loop(
        title="Demo Fase 40",
        description="Rodar ciclo fechado seguro do K-OS sem publicacao, sem IA paga e sem acao externa.",
        priority="high",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=DEFAULT_SAFE_ACTIONS,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
