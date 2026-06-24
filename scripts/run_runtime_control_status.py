from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "local_runtime" / "kos_runtime_control"
LATEST = OUT_DIR / "latest_runtime_control_status_alias.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    target = ROOT / "scripts" / "run_phase49_runtime_control_status.py"
    completed = subprocess.run(
        [sys.executable, str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    payload = {
        "status": "KOS_RUNTIME_CONTROL_STATUS_ALIAS_READY" if completed.returncode == 0 else "KOS_RUNTIME_CONTROL_STATUS_ALIAS_ATTENTION_REQUIRED",
        "created_at": now_iso(),
        "target": str(target),
        "returncode": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-4000:],
        "stderr_tail": (completed.stderr or "")[-4000:],
        "read_only": True,
        "real_action_executed": False,
        "external_side_effects_executed": False,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if completed.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
