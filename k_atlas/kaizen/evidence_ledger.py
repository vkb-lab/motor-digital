from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "evidence"
LEDGER_PATH = LOG_DIR / "evidence_ledger.jsonl"
SUMMARY_PATH = LOG_DIR / "latest_evidence_summary.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _run(cmd: list[str], timeout: int = 30) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[-5000:],
            "stderr": (proc.stderr or "")[-5000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def _read_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            return {"error": str(exc), "path": str(path)}
    return default

def _append_jsonl(path: Path, item: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_git_status() -> dict:
    return {
        "branch": _run(["git", "branch", "--show-current"]).get("stdout", "").strip(),
        "status_short": _run(["git", "--no-pager", "status", "--short"]).get("stdout", ""),
        "last_commit": _run(["git", "--no-pager", "log", "--oneline", "-1"]).get("stdout", "").strip(),
    }

def build_evidence_entry(source: str = "manual", note: str = "", extra: dict | None = None) -> dict:
    health_path = ROOT / "logs" / "kaizen" / "health" / "last_health.json"
    briefing_path = ROOT / "logs" / "kaizen" / "briefing" / "daily_briefing_latest.json"
    scheduler_path = ROOT / "logs" / "kaizen" / "briefing_scheduler" / "last_briefing_scheduler_tick.json"
    startup_path = ROOT / "local_runtime" / "kaizen" / "startup_folder_status.json"

    health = _read_json(health_path, {})
    briefing = _read_json(briefing_path, {})
    scheduler = _read_json(scheduler_path, {})
    startup = _read_json(startup_path, {})
    git = get_git_status()

    runtime_locks = health.get("runtime_locks", {}) if isinstance(health, dict) else {}

    entry = {
        "status": "KOS_AUTONOMY_EVIDENCE_RECORDED",
        "evidence_id": "KOS-EVIDENCE-" + uuid.uuid4().hex[:12].upper(),
        "source": source,
        "note": note,
        "created_at": now(),
        "git": {
            "branch": git.get("branch"),
            "dirty": bool((git.get("status_short") or "").strip()),
            "status_short": git.get("status_short"),
            "last_commit": git.get("last_commit"),
        },
        "health": {
            "health_status": health.get("health_status"),
            "warnings": health.get("warnings", []),
            "startup_installed": health.get("startup_folder", {}).get("installed"),
            "background_running": health.get("background_processes", {}).get("running"),
            "scheduler_tick_exists": health.get("scheduler_last_tick", {}).get("exists"),
        },
        "briefing": {
            "status": briefing.get("status"),
            "risk_level": briefing.get("risk_level"),
            "health_status": briefing.get("health_status"),
            "priorities": briefing.get("priorities", []),
        },
        "scheduler": {
            "status": scheduler.get("status"),
            "cycle_id": scheduler.get("cycle_id"),
            "created_at": scheduler.get("created_at"),
        },
        "startup": {
            "installed": startup.get("installed"),
            "entry_path": startup.get("entry_path"),
        },
        "locks": {
            "production_publish_locked": runtime_locks.get("production_publish_locked", True),
            "paid_ai_locked": runtime_locks.get("paid_ai_locked", True),
            "parada_atlantida_locked": runtime_locks.get("parada_atlantida_locked", True),
            "hupmix_test_only": runtime_locks.get("hupmix_test_only", True),
        },
        "extra": extra or {},
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
    }

    return entry

def append_evidence(source: str = "manual", note: str = "", extra: dict | None = None) -> dict:
    entry = build_evidence_entry(source=source, note=note, extra=extra)
    _append_jsonl(LEDGER_PATH, entry)
    summary = summarize_evidence(limit=10)
    _write_json(SUMMARY_PATH, summary)
    return entry

def summarize_evidence(limit: int = 10) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    if LEDGER_PATH.exists():
        lines = LEDGER_PATH.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass

    latest = entries[-1] if entries else {}

    return {
        "status": "KOS_EVIDENCE_LEDGER_SUMMARY",
        "ledger_exists": LEDGER_PATH.exists(),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)).replace("\\", "/"),
        "entries_returned": len(entries),
        "latest_evidence_id": latest.get("evidence_id"),
        "latest_source": latest.get("source"),
        "latest_health_status": latest.get("health", {}).get("health_status"),
        "latest_risk_level": latest.get("briefing", {}).get("risk_level"),
        "latest_git_dirty": latest.get("git", {}).get("dirty"),
        "last_entries": entries,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

if __name__ == "__main__":
    item = append_evidence(source="phase48_manual", note="manual evidence ledger run")
    print(json.dumps({
        "recorded": item,
        "summary": summarize_evidence(),
    }, ensure_ascii=False, indent=2))
