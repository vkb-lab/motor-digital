from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / "local_runtime" / "kos_chatgpt_bridge"
OUT_DIR = BRIDGE_DIR
LATEST = OUT_DIR / "latest_runtime_status_alias.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def count_files(path: Path, pattern: str = "*") -> int:
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def main() -> int:
    payload = {
        "status": "KOS_CHATGPT_BRIDGE_RUNTIME_STATUS_READY",
        "created_at": now_iso(),
        "drop_dir": str(BRIDGE_DIR / "drop"),
        "processed_dir": str(BRIDGE_DIR / "processed"),
        "blocked_dir": str(BRIDGE_DIR / "blocked"),
        "drop_count": count_files(BRIDGE_DIR / "drop", "*.txt"),
        "processed_count": count_files(BRIDGE_DIR / "processed"),
        "blocked_count": count_files(BRIDGE_DIR / "blocked"),
        "watcher_state": read_json(BRIDGE_DIR / "watcher_state.json"),
        "latest_watcher_event": read_json(BRIDGE_DIR / "latest_watcher_event.json"),
        "read_only": True,
        "browser_logged_account_automation_used": False,
        "browser_scraping_enabled": False,
        "real_action_executed": False,
        "external_side_effects_executed": False,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
