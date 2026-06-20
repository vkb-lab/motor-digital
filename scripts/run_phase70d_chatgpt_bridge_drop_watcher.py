from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

DROP_DIR = ROOT / "local_runtime" / "kos_chatgpt_bridge" / "drop"
PROCESSED_DIR = ROOT / "local_runtime" / "kos_chatgpt_bridge" / "processed"
BLOCKED_DIR = ROOT / "local_runtime" / "kos_chatgpt_bridge" / "blocked"
EVENTS_DIR = ROOT / "local_runtime" / "kos_chatgpt_bridge" / "events"
STATE_FILE = ROOT / "local_runtime" / "kos_chatgpt_bridge" / "watcher_state.json"
LATEST_EVENT = ROOT / "local_runtime" / "kos_chatgpt_bridge" / "latest_watcher_event.json"

REQUIRED_START = "KOS_ENGINEER_PACKET_START"
REQUIRED_END = "KOS_ENGINEER_PACKET_END"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {
            "processed_hashes": [],
            "blocked_hashes": [],
            "events": [],
            "created_at": now_iso(),
        }

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return {
            "processed_hashes": [],
            "blocked_hashes": [],
            "events": [],
            "created_at": now_iso(),
            "state_recovered": True,
        }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_state(state: dict[str, Any]) -> None:
    write_json(STATE_FILE, state)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_name(path: Path) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in path.name)


def candidate_files() -> list[Path]:
    DROP_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(DROP_DIR.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)


def validate_packet_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        return {
            "ok": False,
            "reason": "read_failed",
            "error": str(exc),
        }

    if REQUIRED_START not in text or REQUIRED_END not in text:
        return {
            "ok": False,
            "reason": "missing_packet_markers",
        }

    blocked_terms = [
        "access_token",
        "password",
        "secret",
        "api_key",
        "paradaatlantida",
        "17841480166187766",
        "--execute-real-publish",
        "KOS_REAL_HUPMIX_PUBLISH_ENABLED",
        "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW",
    ]

    low = text.lower()
    hits = [term for term in blocked_terms if term.lower() in low]

    if hits:
        return {
            "ok": False,
            "reason": "blocked_terms_detected",
            "blocked_terms": hits,
        }

    return {
        "ok": True,
        "size_chars": len(text),
    }


def run_command(args: list[str], timeout: int = 240) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=timeout,
    )

    return {
        "returncode": result.returncode,
        "stdout_preview": result.stdout[-5000:],
        "stderr_preview": result.stderr[-5000:],
    }


def process_file(path: Path) -> dict[str, Any]:
    h = file_hash(path)
    validation = validate_packet_file(path)

    event = {
        "status": "KOS_CHATGPT_BRIDGE_DROP_WATCHER_EVENT_CREATED",
        "phase": "70D",
        "file": str(path),
        "file_name": path.name,
        "file_sha256": h,
        "validation": validation,
        "auto_execution_enabled": False,
        "operator_review_required": True,
        "browser_logged_account_automation_used": False,
        "browser_scraping_enabled": False,
        "browser_click_automation_enabled": False,
        "reads_chatgpt_ui_automatically": False,
        "instagram_publish_executed": False,
        "real_action_executed": False,
        "created_at": now_iso(),
    }

    state = read_state()

    if h in state.get("processed_hashes", []) or h in state.get("blocked_hashes", []):
        event["status"] = "KOS_CHATGPT_BRIDGE_DROP_WATCHER_SKIPPED_ALREADY_SEEN"
        return event

    if not validation.get("ok"):
        BLOCKED_DIR.mkdir(parents=True, exist_ok=True)
        blocked_path = BLOCKED_DIR / f"blocked_{stamp()}_{safe_name(path)}"
        shutil.copy2(path, blocked_path)

        state.setdefault("blocked_hashes", []).append(h)
        state.setdefault("events", []).append(event)
        write_state(state)

        event["status"] = "KOS_CHATGPT_BRIDGE_DROP_WATCHER_PACKET_BLOCKED"
        event["blocked_copy"] = str(blocked_path)
        return event

    oneclick = run_command([
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "scripts\\run_kos_engineer_packet_oneclick.ps1",
        "-File",
        str(path),
        "-NoQueueTick",
    ])

    review = run_command([
        "python",
        "scripts\\run_phase69l_engineer_packet_review_console.py",
    ])

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed_path = PROCESSED_DIR / f"processed_{stamp()}_{safe_name(path)}"
    shutil.copy2(path, processed_path)

    event["oneclick"] = oneclick
    event["review"] = review
    event["processed_copy"] = str(processed_path)

    if oneclick["returncode"] == 0 and review["returncode"] == 0:
        event["status"] = "KOS_CHATGPT_BRIDGE_DROP_WATCHER_PACKET_PROCESSED"
        state.setdefault("processed_hashes", []).append(h)
    else:
        event["status"] = "KOS_CHATGPT_BRIDGE_DROP_WATCHER_PACKET_ATTENTION_REQUIRED"
        state.setdefault("blocked_hashes", []).append(h)

    state.setdefault("events", []).append({
        "file": str(path),
        "file_sha256": h,
        "status": event["status"],
        "created_at": event["created_at"],
    })

    write_state(state)
    return event


def run_once(limit: int = 5) -> dict[str, Any]:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)

    processed = []
    files = candidate_files()[:limit]

    for path in files:
        event = process_file(path)
        processed.append(event)

        event_file = EVENTS_DIR / f"event_{stamp()}_{safe_name(path)}.json"
        write_json(event_file, event)
        write_json(LATEST_EVENT, event)

    result = {
        "status": "KOS_CHATGPT_BRIDGE_DROP_WATCHER_TICK_COMPLETED",
        "phase": "70D",
        "drop_dir": str(DROP_DIR),
        "processed_count": len(processed),
        "events": processed,
        "auto_execution_enabled": False,
        "operator_review_required": True,
        "browser_logged_account_automation_used": False,
        "browser_scraping_enabled": False,
        "browser_click_automation_enabled": False,
        "reads_chatgpt_ui_automatically": False,
        "instagram_publish_executed": False,
        "real_action_executed": False,
        "created_at": now_iso(),
    }

    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--poll-seconds", type=int, default=5)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if args.loop:
        print(json.dumps({
            "status": "KOS_CHATGPT_BRIDGE_DROP_WATCHER_LOOP_STARTED",
            "phase": "70D",
            "drop_dir": str(DROP_DIR),
            "poll_seconds": args.poll_seconds,
            "auto_execution_enabled": False,
            "operator_review_required": True,
            "created_at": now_iso(),
        }, indent=2, ensure_ascii=False), flush=True)

        while True:
            result = run_once(limit=args.limit)
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
            time.sleep(max(2, args.poll_seconds))

    result = run_once(limit=args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
