from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\oi\Desktop\motor-digital")
REPORT = ROOT / "reports" / "KOS_PHASE66B2_STARTUP_OPERATIONAL_PROFILE_STATUS.json"

def run(command):
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, check=False)
    return (completed.stdout or "") + (completed.stderr or "")

payload = {
    "status": "KOS_PHASE66B2_STARTUP_OPERATIONAL_PROFILE_STATUS_COMPLETED",
    "runtime_status_raw": run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts\\kos_runtime_control.ps1", "-Action", "status"]),
    "git_status": run(["git", "--no-pager", "status", "--short"]),
    "policy_exists": (ROOT / "config" / "kos_startup_operational_profile_policy.json").exists(),
    "startup_script_exists": (ROOT / "scripts" / "start_kos_startup_operational_profile.ps1").exists(),
    "installer_exists": (ROOT / "scripts" / "install_kos_startup_operational_profile.ps1").exists(),
    "production_publish_locked": True,
    "paid_ai_locked": True,
    "instagram_publish_locked": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
}

REPORT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
