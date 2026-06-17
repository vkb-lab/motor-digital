
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

from k_atlas.kaizen.engineer_handoff_bridge import stage_engineer_response, get_engineer_handoff_status

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "local_runtime" / "kos_engineer_handoff"
INBOX = RUNTIME / "inbox"
PROCESSED = RUNTIME / "processed"
DUPLICATES = RUNTIME / "duplicates"
BLOCKED = RUNTIME / "blocked"
LOGS = RUNTIME / "logs"
LATEST = RUNTIME / "latest_engineer_handoff_queue_status.json"
EVENTS = LOGS / "queue_events.jsonl"

SUPPORTED_SUFFIXES = {".txt", ".ps1", ".md"}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_event(data: dict) -> None:
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return path.as_posix().replace("\\", "/")

def move_to_bucket(path: Path, bucket: Path) -> str:
    bucket.mkdir(parents=True, exist_ok=True)
    target = bucket / path.name
    if target.exists():
        target = bucket / f"{path.stem}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}{path.suffix}"
    shutil.move(str(path), str(target))
    return rel(target)

def list_handoff_inbox_files(limit: int = 20) -> list[Path]:
    INBOX.mkdir(parents=True, exist_ok=True)
    files = [p for p in INBOX.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES]
    return sorted(files, key=lambda p: p.stat().st_mtime)[:limit]

def process_engineer_handoff_queue(limit: int = 10) -> dict:
    files = list_handoff_inbox_files(limit=limit)
    processed = []

    for path in files:
        try:
            text = path.read_text(encoding="utf-8-sig")
            result = stage_engineer_response(text, title=path.stem)

            if result.get("duplicate_skipped"):
                bucket_path = move_to_bucket(path, DUPLICATES)
                bucket = "duplicates"
            elif result.get("safe_for_confirmed_execution") is True:
                bucket_path = move_to_bucket(path, PROCESSED)
                bucket = "processed"
            else:
                bucket_path = move_to_bucket(path, BLOCKED)
                bucket = "blocked"

            item = {
                "status": "ENGINEER_HANDOFF_QUEUE_ITEM_PROCESSED",
                "source_file": path.name,
                "bucket": bucket,
                "bucket_path": bucket_path,
                "stage_status": result.get("status"),
                "draft_id": result.get("draft_id"),
                "safe": result.get("safe_for_confirmed_execution"),
                "duplicate_skipped": result.get("duplicate_skipped", False),
                "confirmed_execution_command": result.get("confirmed_execution_command"),
                "created_at": now()
            }
        except Exception as exc:
            bucket_path = move_to_bucket(path, BLOCKED)
            item = {
                "status": "ENGINEER_HANDOFF_QUEUE_ITEM_ERROR",
                "source_file": path.name,
                "bucket": "blocked",
                "bucket_path": bucket_path,
                "error": str(exc),
                "created_at": now()
            }

        append_event(item)
        processed.append(item)

    bridge_status = get_engineer_handoff_status()

    payload = {
        "status": "ENGINEER_HANDOFF_QUEUE_PROCESSED",
        "inbox_seen": len(files),
        "processed_count": len(processed),
        "items": processed,
        "bridge_status": bridge_status.get("status"),
        "staged_commands_count": bridge_status.get("staged_commands_count"),
        "gates": {
            "no_browser_click_required": True,
            "duplicate_guard": True,
            "execute_without_confirmation": False,
            "human_confirmation_required": True,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now()
    }

    write_json(LATEST, payload)
    append_event(payload)
    return payload

def write_orchestrator_inbox_command(command_text: str, title: str = "engineer_command") -> dict:
    INBOX.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title).strip("_") or "engineer_command"
    path = INBOX / f"{safe_title}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.ps1"
    path.write_text(command_text, encoding="utf-8")
    return {
        "status": "ENGINEER_HANDOFF_INBOX_COMMAND_WRITTEN",
        "path": rel(path),
        "created_at": now(),
        "real_action_executed": False
    }

def get_engineer_handoff_queue_status() -> dict:
    if LATEST.exists():
        try:
            return json.loads(LATEST.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    return process_engineer_handoff_queue(limit=0)
