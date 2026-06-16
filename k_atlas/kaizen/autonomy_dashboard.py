from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "dashboard"

SENSITIVE_KEYS = [
    "TOKEN",
    "KEY",
    "SECRET",
    "PASSWORD",
    "ACCESS",
    "AUTH",
    "BEARER",
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_cmd(cmd: list[str], timeout: int = 20) -> dict:
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
            "stdout": (proc.stdout or "")[-4000:],
            "stderr": (proc.stderr or "")[-4000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def detect_tool(name: str) -> dict:
    path = shutil.which(name)
    if not path:
        return {
            "installed": False,
            "path": "",
            "version": ""
        }

    version = run_cmd([name, "--version"], timeout=20)
    return {
        "installed": True,
        "path": path,
        "version": ((version.get("stdout") or "") + (version.get("stderr") or "")).strip()
    }

def read_json(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            return {
                "error": str(exc),
                "path": str(path)
            }
    return default

def redact_line(line: str) -> str:
    upper = line.upper()
    if "=" in line and any(key in upper for key in SENSITIVE_KEYS):
        key = line.split("=", 1)[0]
        return f"{key}=<redacted>"
    return line

def read_redacted_env(path: Path) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "lines": []
        }

    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    return {
        "exists": True,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "lines": [redact_line(line) for line in lines]
    }

def get_git_summary() -> dict:
    return {
        "branch": run_cmd(["git", "branch", "--show-current"]).get("stdout", "").strip(),
        "status_short": run_cmd(["git", "--no-pager", "status", "--short"]).get("stdout", ""),
        "last_commits": run_cmd(["git", "--no-pager", "log", "--oneline", "-5"]).get("stdout", ""),
    }

def get_mission_summary() -> dict:
    try:
        from k_atlas.kaizen.mission_queue import summarize_queue
        return summarize_queue()
    except Exception as exc:
        return {"error": str(exc)}

def get_approval_summary() -> dict:
    try:
        from k_atlas.kaizen.human_approval import summarize_approvals
        return summarize_approvals()
    except Exception as exc:
        return {"error": str(exc)}

def get_safe_executor_summary() -> dict:
    try:
        from k_atlas.kaizen.safe_executor import list_safe_actions
        return {
            "allowed_actions": list_safe_actions(),
            "mode": "SANDBOX_ONLY"
        }
    except Exception as exc:
        return {"error": str(exc)}

def get_closed_loop_summary() -> dict:
    try:
        from k_atlas.kaizen.closed_loop import summarize_last_reports
        return summarize_last_reports()
    except Exception as exc:
        return {"error": str(exc)}

def get_runtime_locks() -> dict:
    ig_runtime = read_redacted_env(ROOT / "local_runtime" / "ig_runtime.env")
    ai_runtime = read_redacted_env(ROOT / "local_runtime" / "ai_runtime.env")

    joined_ig = "\n".join(ig_runtime.get("lines", []))
    joined_ai = "\n".join(ai_runtime.get("lines", []))

    return {
        "ig_runtime": ig_runtime,
        "ai_runtime": ai_runtime,
        "production_publish_enabled_seen": "KOS_REAL_IG_PUBLISH_ENABLED=true" in joined_ig,
        "production_publish_locked": "KOS_REAL_IG_PUBLISH_ENABLED=true" not in joined_ig,
        "paid_ai_enabled_seen": (
            "KOS_AI_OPENAI_ENABLED=true" in joined_ai or
            "KOS_AI_GEMINI_ENABLED=true" in joined_ai
        ),
        "paid_ai_locked": not (
            "KOS_AI_OPENAI_ENABLED=true" in joined_ai or
            "KOS_AI_GEMINI_ENABLED=true" in joined_ai
        ),
        "parada_atlantida_locked": True,
        "hupmix_test_only": True,
    }

def build_autonomy_snapshot(write_log: bool = True) -> dict:
    snapshot = {
        "status": "KOS_AUTONOMY_DASHBOARD_SNAPSHOT",
        "mode": "READ_ONLY_OPERATIONAL_COCKPIT",
        "created_at": now(),
        "git": get_git_summary(),
        "tools": {
            "codex": detect_tool("codex"),
            "ollama": detect_tool("ollama"),
        },
        "runtime_locks": get_runtime_locks(),
        "mission_queue": get_mission_summary(),
        "human_approval": get_approval_summary(),
        "safe_executor": get_safe_executor_summary(),
        "closed_loop": get_closed_loop_summary(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
    }

    if write_log:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = LOG_DIR / "last_snapshot.json"
        path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    return snapshot

if __name__ == "__main__":
    print(json.dumps(build_autonomy_snapshot(), ensure_ascii=False, indent=2))
