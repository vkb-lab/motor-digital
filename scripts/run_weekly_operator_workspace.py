from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="summary")
    args = parser.parse_args()

    target = ROOT / "scripts" / "run_phase72a_weekly_operator_workspace.py"
    completed = subprocess.run(
        [sys.executable, str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
    )

    payload = {
        "status": "KOS_WEEKLY_OPERATOR_WORKSPACE_ALIAS_READY" if completed.returncode == 0 else "KOS_WEEKLY_OPERATOR_WORKSPACE_ALIAS_ATTENTION_REQUIRED",
        "created_at": now_iso(),
        "mode": args.mode,
        "target": str(target),
        "returncode": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-4000:],
        "stderr_tail": (completed.stderr or "")[-4000:],
        "real_action_executed": False,
        "external_side_effects_executed": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if completed.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
