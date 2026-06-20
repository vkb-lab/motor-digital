from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

LATEST_ONECLICK = ROOT / "local_runtime" / "kos_engineer_command_intake" / "latest_oneclick_result.json"
LATEST_PROMOTION = ROOT / "local_runtime" / "kos_engineer_command_intake" / "latest_promotion_result.json"
REVIEW_DIR = ROOT / "local_runtime" / "kos_engineer_packet_review"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "FILE_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_FAILED", "path": str(path), "error": str(exc)}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def run_queue_tick() -> dict[str, Any]:
    script = ROOT / "scripts" / "run_phase66b_engineer_handoff_queue.py"
    if not script.exists():
        return {
            "status": "KOS_ENGINEER_PACKET_REVIEW_QUEUE_TICK_SKIPPED",
            "reason": "queue_script_not_found",
        }

    result = subprocess.run(
        ["python", str(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=180,
    )

    return {
        "status": "KOS_ENGINEER_PACKET_REVIEW_QUEUE_TICK_EXECUTED",
        "returncode": result.returncode,
        "stdout_preview": result.stdout[-3000:],
        "stderr_preview": result.stderr[-3000:],
    }


def list_recent_json(folder: Path, limit: int = 8) -> list[dict[str, Any]]:
    if not folder.exists():
        return []
    files = sorted(folder.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    items = []
    for path in files:
        payload = read_json(path)
        items.append({
            "path": str(path),
            "status": payload.get("status"),
            "title": payload.get("title"),
            "packet_id": payload.get("packet_id"),
            "command_hash": payload.get("command_hash"),
            "created_at": payload.get("created_at"),
        })
    return items


def build_review(run_tick: bool = True) -> dict[str, Any]:
    oneclick = read_json(LATEST_ONECLICK)
    promotion = read_json(LATEST_PROMOTION)

    queue_tick = run_queue_tick() if run_tick else {
        "status": "KOS_ENGINEER_PACKET_REVIEW_QUEUE_TICK_SKIPPED_BY_OPERATOR"
    }

    handoff_root = ROOT / "local_runtime" / "kos_engineer_handoff"

    review = {
        "status": "KOS_ENGINEER_PACKET_REVIEW_READY",
        "phase": "69L",
        "oneclick_status": oneclick.get("status"),
        "packet_id": oneclick.get("packet_id") or promotion.get("packet_id"),
        "promotion_status": promotion.get("status"),
        "handoff_inbox_file": promotion.get("handoff_inbox_file") or oneclick.get("handoff_inbox_file"),
        "queue_tick": queue_tick,
        "recent_handoff_items": {
            "inbox": list_recent_json(handoff_root / "inbox"),
            "processed": list_recent_json(handoff_root / "processed"),
            "staged": list_recent_json(handoff_root / "staged"),
            "staged_commands": list_recent_json(handoff_root / "staged_commands"),
            "blocked": list_recent_json(handoff_root / "blocked"),
            "duplicates": list_recent_json(handoff_root / "duplicates"),
        },
        "operator_next_action": "revisar no KOS Engineer Handoff/Queue antes de qualquer execucao",
        "auto_execution_enabled": False,
        "operator_review_required": True,
        "execution_requires_existing_approval_pipeline": True,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "real_action_executed": False,
        "created_at": now_iso(),
    }

    write_json(REVIEW_DIR / "latest_engineer_packet_review.json", review)
    return review


def main() -> int:
    review = build_review(run_tick=True)
    print(json.dumps(review, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
