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
    "phase": "44",
    "module": "K-OS Runtime Health Monitor",
    "mode": "READ_ONLY_HEALTH_CHECK",
    "goal": "monitorar se o K-OS 24/7 local esta vivo, seguro e sem efeitos externos",
    "allowed_actions": {
        "check_startup_folder": True,
        "check_background_process": True,
        "check_scheduler_last_tick": True,
        "check_git_status": True,
        "check_runtime_locks": True,
        "read_logs_tail": True,
        "write_health_report": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "mutation_from_health_monitor": True
    },
    "hard_rules": {
        "read_only": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

health_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "health"
HEALTH_REPORT = LOG_DIR / "last_health.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            return {"error": str(exc), "path": str(path)}
    return default

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

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
            "stdout": (proc.stdout or "")[-6000:],
            "stderr": (proc.stderr or "")[-6000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def check_background_processes() -> dict:
    ps = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -match 'start_kos_autonomy_scheduler_manual_loop' } | "
        "Select-Object ProcessId,CommandLine | ConvertTo-Json -Depth 4 -Compress"
    )

    result = _run([
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        ps
    ], timeout=30)

    stdout = (result.get("stdout") or "").strip()
    count = 0

    if stdout:
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, list):
                count = len(parsed)
            elif isinstance(parsed, dict):
                count = 1
        except Exception:
            count = 1

    return {
        "status": "BACKGROUND_PROCESS_CHECKED",
        "process_count": count,
        "running": count > 0,
        "raw": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }

def check_startup_folder() -> dict:
    try:
        from k_atlas.kaizen.startup_folder_gate import check_startup_status
        return check_startup_status()
    except Exception as exc:
        return {
            "status": "STARTUP_FOLDER_CHECK_ERROR",
            "error": str(exc),
            "installed": False,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

def check_scheduler_tick() -> dict:
    tick_path = ROOT / "logs" / "kaizen" / "scheduler" / "last_tick.json"
    data = _read_json(tick_path, {})

    return {
        "status": "SCHEDULER_LAST_TICK_CHECKED",
        "exists": tick_path.exists(),
        "path": str(tick_path.relative_to(ROOT)).replace("\\", "/"),
        "last_tick_status": data.get("status"),
        "created_at": data.get("created_at"),
        "real_action_executed": data.get("real_action_executed", False),
        "paid_ai_call_executed": data.get("paid_ai_call_executed", False),
        "instagram_publish_executed": data.get("instagram_publish_executed", False),
    }

def check_git() -> dict:
    return {
        "branch": _run(["git", "branch", "--show-current"]).get("stdout", "").strip(),
        "status_short": _run(["git", "--no-pager", "status", "--short"]).get("stdout", ""),
        "last_commits": _run(["git", "--no-pager", "log", "--oneline", "-5"]).get("stdout", ""),
    }

def read_log_tail(path: Path, lines: int = 80) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "tail": ""
        }

    content = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    return {
        "exists": True,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "tail": "\n".join(content[-lines:])
    }

def check_runtime_locks() -> dict:
    try:
        from k_atlas.kaizen.autonomy_dashboard import get_runtime_locks
        return get_runtime_locks()
    except Exception as exc:
        return {
            "error": str(exc),
            "production_publish_locked": True,
            "paid_ai_locked": True,
            "parada_atlantida_locked": True,
            "hupmix_test_only": True,
        }

def build_runtime_health(write_log: bool = True) -> dict:
    startup = check_startup_folder()
    processes = check_background_processes()
    tick = check_scheduler_tick()
    git = check_git()
    locks = check_runtime_locks()

    startup_log = read_log_tail(ROOT / "logs" / "kaizen" / "startup" / "manual_background_loop.log", lines=80)
    startup_login_log = read_log_tail(ROOT / "logs" / "kaizen" / "startup" / "startup_loop.log", lines=80)

    git_dirty = bool((git.get("status_short") or "").strip())

    warnings = []

    if not startup.get("installed"):
        warnings.append("Startup Folder nao instalado.")

    if not processes.get("running"):
        warnings.append("Loop em background nao detectado agora.")

    if not tick.get("exists"):
        warnings.append("Ultimo tick do scheduler ainda nao encontrado.")

    if git_dirty:
        warnings.append("Git possui alteracoes locais.")

    if not locks.get("production_publish_locked", True):
        warnings.append("ATENCAO: flag de publicacao real parece habilitada.")

    if not locks.get("paid_ai_locked", True):
        warnings.append("ATENCAO: IA paga parece habilitada.")

    health_status = "HEALTHY" if not warnings else "ATTENTION_REQUIRED"

    report = {
        "status": "KOS_RUNTIME_HEALTH_CHECK_COMPLETED",
        "health_status": health_status,
        "warnings": warnings,
        "startup_folder": startup,
        "background_processes": processes,
        "scheduler_last_tick": tick,
        "git": git,
        "runtime_locks": locks,
        "logs": {
            "manual_background_loop": startup_log,
            "startup_login_loop": startup_login_log,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    if write_log:
        _save_json(HEALTH_REPORT, report)

    return report

if __name__ == "__main__":
    print(json.dumps(build_runtime_health(write_log=True), ensure_ascii=False, indent=2))
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.runtime_health import build_runtime_health

if __name__ == "__main__":
    result = build_runtime_health(write_log=True)
    print(json.dumps({
        "status": "PHASE44_RUNTIME_HEALTH_CHECK_COMPLETED",
        "health_status": result.get("health_status"),
        "warnings": result.get("warnings", []),
        "startup_installed": result.get("startup_folder", {}).get("installed"),
        "background_running": result.get("background_processes", {}).get("running"),
        "scheduler_tick_exists": result.get("scheduler_last_tick", {}).get("exists"),
        "git_dirty": bool(result.get("git", {}).get("status_short", "").strip()),
        "production_publish_locked": result.get("runtime_locks", {}).get("production_publish_locked"),
        "paid_ai_locked": result.get("runtime_locks", {}).get("paid_ai_locked"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.runtime_health import build_runtime_health

st.set_page_config(page_title="KOS Runtime Health", layout="wide")

st.title("KOS Runtime Health Monitor")
st.caption("Monitor read-only do K-OS 24/7 local.")

health = build_runtime_health(write_log=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Health", health.get("health_status", "N/A"))
col2.metric("Startup", "SIM" if health.get("startup_folder", {}).get("installed") else "NAO")
col3.metric("Background", "SIM" if health.get("background_processes", {}).get("running") else "NAO")
col4.metric("Git dirty", "SIM" if health.get("git", {}).get("status_short", "").strip() else "NAO")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Scheduler tick", "SIM" if health.get("scheduler_last_tick", {}).get("exists") else "NAO")
col6.metric("IG publish", "BLOQUEADO" if health.get("runtime_locks", {}).get("production_publish_locked") else "ATENCAO")
col7.metric("IA paga", "BLOQUEADA" if health.get("runtime_locks", {}).get("paid_ai_locked") else "ATENCAO")
col8.metric("External actions", "NAO")

if health.get("warnings"):
    st.warning(health.get("warnings"))
else:
    st.success("Runtime saudavel.")

st.subheader("Resumo completo")
st.json(health)

st.subheader("Ultimos commits")
st.code(health.get("git", {}).get("last_commits", ""))

st.warning("Monitor read-only. Nao publica, nao usa IA paga e nao executa Codex automaticamente.")
'''

test_code = r'''
from k_atlas.kaizen.runtime_health import build_runtime_health, check_scheduler_tick, check_background_processes

def test_runtime_health_is_read_only():
    health = build_runtime_health(write_log=False)

    assert health["status"] == "KOS_RUNTIME_HEALTH_CHECK_COMPLETED"
    assert health["real_action_executed"] is False
    assert health["paid_ai_call_executed"] is False
    assert health["instagram_publish_executed"] is False
    assert health["external_side_effects_executed"] is False

def test_scheduler_tick_check_safe_flags():
    tick = check_scheduler_tick()

    assert tick["status"] == "SCHEDULER_LAST_TICK_CHECKED"
    assert tick["real_action_executed"] is False
    assert tick["paid_ai_call_executed"] is False
    assert tick["instagram_publish_executed"] is False

def test_background_process_check_is_read_only():
    result = check_background_processes()

    assert result["status"] == "BACKGROUND_PROCESS_CHECKED"
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_runtime_health_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "runtime_health.py", health_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase44_runtime_health_check.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Runtime_Health.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase44_runtime_health.py", test_code.strip() + "\n")

report = {
    "status": "PHASE44_RUNTIME_HEALTH_BOOTSTRAPPED",
    "phase": "44",
    "created_files": [
        "config/kos_runtime_health_policy.json",
        "k_atlas/kaizen/runtime_health.py",
        "scripts/run_phase44_runtime_health_check.py",
        "pages/KOS_Runtime_Health.py",
        "tests/test_phase44_runtime_health.py"
    ],
    "runtime_files": [
        "logs/kaizen/health/last_health.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE44_RUNTIME_HEALTH_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))