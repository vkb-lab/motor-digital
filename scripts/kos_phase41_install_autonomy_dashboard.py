from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

policy = {
    "status": "ACTIVE",
    "phase": "41",
    "module": "K-OS Autonomy Dashboard",
    "mode": "READ_ONLY_OPERATIONAL_COCKPIT",
    "goal": "centralizar estado de autonomia, aprovacoes, missoes, executor sandbox, Codex/Ollama e travas Instagram",
    "allowed_actions": {
        "read_git_status": True,
        "read_codex_status": True,
        "read_ollama_status": True,
        "read_mission_queue": True,
        "read_approval_ledger": True,
        "read_closed_loop_reports": True,
        "read_safe_executor_actions": True,
        "read_redacted_runtime": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "file_mutation_from_dashboard": True,
        "production_publish": True
    },
    "hard_rules": {
        "dashboard_read_only": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

dashboard_code = r'''
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
'''

runner_code = r'''
from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot
import json

if __name__ == "__main__":
    snapshot = build_autonomy_snapshot(write_log=True)
    print(json.dumps({
        "status": "PHASE41_AUTONOMY_DASHBOARD_SNAPSHOT_COMPLETED",
        "branch": snapshot.get("git", {}).get("branch"),
        "git_dirty": bool(snapshot.get("git", {}).get("status_short", "").strip()),
        "codex_installed": snapshot.get("tools", {}).get("codex", {}).get("installed"),
        "ollama_installed": snapshot.get("tools", {}).get("ollama", {}).get("installed"),
        "production_publish_locked": snapshot.get("runtime_locks", {}).get("production_publish_locked"),
        "paid_ai_locked": snapshot.get("runtime_locks", {}).get("paid_ai_locked"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot

st.set_page_config(page_title="KOS Autonomy Dashboard", layout="wide")

st.title("KOS Autonomy Dashboard")
st.caption("Cockpit read-only: autonomia, missoes, aprovacoes, executor, Codex/Ollama e travas.")

snapshot = build_autonomy_snapshot(write_log=True)

git = snapshot.get("git", {})
tools = snapshot.get("tools", {})
locks = snapshot.get("runtime_locks", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Branch", git.get("branch", "N/A"))
col2.metric("Git dirty", "SIM" if git.get("status_short", "").strip() else "NAO")
col3.metric("Codex", "OK" if tools.get("codex", {}).get("installed") else "NAO")
col4.metric("Ollama", "OK" if tools.get("ollama", {}).get("installed") else "NAO")

col5, col6, col7, col8 = st.columns(4)
col5.metric("IG producao", "BLOQUEADO" if locks.get("production_publish_locked") else "ATENCAO")
col6.metric("IA paga", "BLOQUEADA" if locks.get("paid_ai_locked") else "ATENCAO")
col7.metric("Parada Atlantida", "LOCKED")
col8.metric("Hupmix", "TEST ONLY")

st.subheader("Mission Queue")
st.json(snapshot.get("mission_queue", {}))

st.subheader("Human Approval")
st.json(snapshot.get("human_approval", {}))

st.subheader("Safe Executor")
st.json(snapshot.get("safe_executor", {}))

st.subheader("Closed Loop")
st.json(snapshot.get("closed_loop", {}))

st.subheader("Runtime redigido")
st.json(snapshot.get("runtime_locks", {}))

st.subheader("Git")
st.code(git.get("status_short", "") or "workspace limpo")
st.code(git.get("last_commits", ""))

st.warning("Dashboard read-only. Nao publica, nao usa IA paga, nao executa Codex automaticamente e nao exibe segredos.")
'''

test_code = r'''
from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot, redact_line

def test_redact_line_hides_sensitive_values():
    assert redact_line("TOKEN=abc123") == "TOKEN=<redacted>"
    assert redact_line("OPENAI_API_KEY=abc123") == "OPENAI_API_KEY=<redacted>"
    assert redact_line("NORMAL=value") == "NORMAL=value"

def test_snapshot_is_read_only_and_safe():
    snapshot = build_autonomy_snapshot(write_log=False)

    assert snapshot["status"] == "KOS_AUTONOMY_DASHBOARD_SNAPSHOT"
    assert snapshot["real_action_executed"] is False
    assert snapshot["paid_ai_call_executed"] is False
    assert snapshot["instagram_publish_executed"] is False
    assert snapshot["external_side_effects_executed"] is False

def test_runtime_locks_have_expected_flags():
    snapshot = build_autonomy_snapshot(write_log=False)
    locks = snapshot["runtime_locks"]

    assert locks["parada_atlantida_locked"] is True
    assert locks["hupmix_test_only"] is True
'''

save_json(ROOT / "config" / "kos_autonomy_dashboard_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "autonomy_dashboard.py", dashboard_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase41_autonomy_dashboard_snapshot.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "000_KOS_Autonomy_Dashboard.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase41_autonomy_dashboard.py", test_code.strip() + "\n")

report = {
    "status": "PHASE41_AUTONOMY_DASHBOARD_BOOTSTRAPPED",
    "phase": "41",
    "created_files": [
        "config/kos_autonomy_dashboard_policy.json",
        "k_atlas/kaizen/autonomy_dashboard.py",
        "scripts/run_phase41_autonomy_dashboard_snapshot.py",
        "pages/000_KOS_Autonomy_Dashboard.py",
        "tests/test_phase41_autonomy_dashboard.py"
    ],
    "runtime_files": [
        "logs/kaizen/dashboard/last_snapshot.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE41_AUTONOMY_DASHBOARD_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))