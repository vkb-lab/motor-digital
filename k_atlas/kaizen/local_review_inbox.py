from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]

COMMAND_INBOX = ROOT / "local_runtime" / "operator_command_bridge" / "inbox"
TASKS_DIR = ROOT / "local_runtime" / "kos_local_coworker" / "tasks"
WORK_ORDERS_DIR = ROOT / "local_runtime" / "kos_local_patch_workspace" / "work_orders"
COMMAND_DRAFTS_DIR = ROOT / "local_runtime" / "kos_local_command_composer" / "commands"
LOOP_STATUS = ROOT / "local_runtime" / "kos_local_autonomy_loop" / "latest_loop_status.json"

REVIEW_DIR = ROOT / "local_runtime" / "kos_local_review_inbox"
LATEST_REVIEW = REVIEW_DIR / "latest_review_inbox.json"
EVENTS_PATH = REVIEW_DIR / "logs" / "events.jsonl"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _load_json_files(folder: Path, limit: int = 20) -> list[dict]:
    if not folder.exists():
        return []

    paths = sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    items = []

    for path in paths:
        item = _read_json(path)
        if item:
            item["_source_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            items.append(item)

    return items

def summarize_review_items(commands: list[dict], tasks: list[dict], work_orders: list[dict], drafts: list[dict]) -> dict:
    return {
        "commands_count": len(commands),
        "tasks_count": len(tasks),
        "work_orders_count": len(work_orders),
        "command_drafts_count": len(drafts),
        "has_pending_review": len(work_orders) > 0 or len(drafts) > 0,
        "latest_command_title": commands[0].get("title") if commands else None,
        "latest_task_title": tasks[0].get("title") if tasks else None,
        "latest_work_order_title": work_orders[0].get("title") if work_orders else None,
        "latest_command_draft_title": drafts[0].get("title") if drafts else None,
    }

def build_review_bundle(commands: list[dict], tasks: list[dict], work_orders: list[dict], drafts: list[dict], loop_status: dict) -> dict:
    latest_draft = drafts[0] if drafts else {}
    latest_order = work_orders[0] if work_orders else {}
    latest_task = tasks[0] if tasks else {}
    latest_command = commands[0] if commands else {}

    bundle_text = "\n".join([
        "K-OS LOCAL REVIEW BUNDLE",
        "",
        f"Command: {latest_command.get('command_id', 'none')} - {latest_command.get('title', 'none')}",
        f"Task: {latest_task.get('task_id', 'none')} - {latest_task.get('title', 'none')}",
        f"Work Order: {latest_order.get('work_order_id', 'none')} - {latest_order.get('title', 'none')}",
        f"Command Draft: {latest_draft.get('draft_id', 'none')} - {latest_draft.get('title', 'none')}",
        "",
        "LATEST POWERSHELL DRAFT",
        "",
        latest_draft.get("powershell_command", "Nenhum command draft disponivel ainda."),
        "",
        "GATES",
        "",
        "execute_allowed_now=false",
        "repo_write_allowed_now=false",
        "patch_apply_allowed_now=false",
        "commit_allowed=false",
        "push_allowed=false",
        "deploy_allowed=false",
        "paid_ai_allowed=false",
        "instagram_publish_allowed=false",
    ])

    return {
        "status": "KOS_LOCAL_REVIEW_BUNDLE_READY",
        "latest_command": latest_command,
        "latest_task": latest_task,
        "latest_work_order": latest_order,
        "latest_command_draft": latest_draft,
        "loop_status": loop_status,
        "bundle_text": bundle_text,
        "gates": {
            "read_only": True,
            "execute_allowed_now": False,
            "repo_write_allowed_now": False,
            "patch_apply_allowed_now": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "human_review_required": True,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

def collect_review_inbox(limit: int = 20) -> dict:
    commands = _load_json_files(COMMAND_INBOX, limit=limit)
    tasks = _load_json_files(TASKS_DIR, limit=limit)
    work_orders = _load_json_files(WORK_ORDERS_DIR, limit=limit)
    drafts = _load_json_files(COMMAND_DRAFTS_DIR, limit=limit)
    loop_status = _read_json(LOOP_STATUS)

    summary = summarize_review_items(commands, tasks, work_orders, drafts)
    bundle = build_review_bundle(commands, tasks, work_orders, drafts, loop_status)

    payload = {
        "status": "KOS_LOCAL_REVIEW_INBOX_READY",
        "summary": summary,
        "commands": commands,
        "tasks": tasks,
        "work_orders": work_orders,
        "command_drafts": drafts,
        "loop_status": loop_status,
        "review_bundle": bundle,
        "gates": {
            "read_only": True,
            "execute_allowed_now": False,
            "repo_write_allowed_now": False,
            "patch_apply_allowed_now": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    _write_json(LATEST_REVIEW, payload)
    _append_jsonl(EVENTS_PATH, {
        "status": "KOS_LOCAL_REVIEW_INBOX_SAVED",
        "summary": summary,
        "created_at": now(),
        "real_action_executed": False,
    })

    return payload

def get_latest_review_inbox() -> dict:
    if LATEST_REVIEW.exists():
        return _read_json(LATEST_REVIEW)
    return collect_review_inbox(limit=20)

if __name__ == "__main__":
    print(json.dumps(collect_review_inbox(), ensure_ascii=False, indent=2))