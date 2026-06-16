from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = ROOT / "local_runtime" / "kaizen" / "startup_folder_status.json"

ENTRY_NAME = "KOS-Autonomy-Scheduler-Local.cmd"
CONFIRMATION = "YES_REGISTER_KOS_STARTUP_LOCAL_ONLY"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def startup_folder() -> Path:
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

def startup_entry_path() -> Path:
    return startup_folder() / ENTRY_NAME

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def check_startup_status() -> dict:
    folder = startup_folder()
    entry = startup_entry_path()

    status = {
        "status": "STARTUP_FOLDER_STATUS_CHECKED",
        "startup_folder": str(folder),
        "entry_name": ENTRY_NAME,
        "entry_path": str(entry),
        "installed": entry.exists(),
        "confirmation_required": CONFIRMATION,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

    _save_json(STATUS_PATH, status)
    return status

def build_startup_plan() -> dict:
    return {
        "status": "STARTUP_FOLDER_GATE_READY",
        "entry_name": ENTRY_NAME,
        "confirmation_required": CONFIRMATION,
        "register_script": "scripts/register_kos_autonomy_startup_folder.ps1",
        "unregister_script": "scripts/unregister_kos_autonomy_startup_folder.ps1",
        "requires_admin": False,
        "registers_without_confirmation": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

if __name__ == "__main__":
    print(json.dumps({
        "plan": build_startup_plan(),
        "startup_status": check_startup_status()
    }, ensure_ascii=False, indent=2))
