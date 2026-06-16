from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def replace_block(path: Path, start_marker: str, end_marker: str, replacement: str):
    text = path.read_text(encoding="utf-8-sig")
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    new_text = text[:start] + replacement.rstrip() + "\n" + text[end:]
    path.write_text(new_text, encoding="utf-8")

runtime_control_func = r'''
def check_runtime_processes() -> dict:
    ps = r"""
$script = (Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path
$escaped = [regex]::Escape($script)

Get-CimInstance Win32_Process |
  Where-Object {
    $_.ProcessId -ne $PID -and
    $_.CommandLine -and
    $_.CommandLine -match $escaped -and
    $_.CommandLine -notmatch '\s-Command\s'
  } |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  ConvertTo-Json -Depth 4 -Compress
"""

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
            count = 0

    return {
        "status": "RUNTIME_PROCESS_CHECKED",
        "running": count > 0,
        "process_count": count,
        "counting_rule": "counts_only_real_loop_process_excluding_checker_and_command_wrapper",
        "raw": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }
'''

runtime_health_func = r'''
def check_background_processes() -> dict:
    ps = r"""
$script = (Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path
$escaped = [regex]::Escape($script)

Get-CimInstance Win32_Process |
  Where-Object {
    $_.ProcessId -ne $PID -and
    $_.CommandLine -and
    $_.CommandLine -match $escaped -and
    $_.CommandLine -notmatch '\s-Command\s'
  } |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  ConvertTo-Json -Depth 4 -Compress
"""

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
            count = 0

    return {
        "status": "BACKGROUND_PROCESS_CHECKED",
        "process_count": count,
        "running": count > 0,
        "counting_rule": "counts_only_real_loop_process_excluding_checker_and_command_wrapper",
        "raw": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }
'''

replace_block(
    ROOT / "k_atlas" / "kaizen" / "runtime_control.py",
    "def check_runtime_processes() -> dict:",
    "\ndef get_git_summary() -> dict:",
    runtime_control_func
)

replace_block(
    ROOT / "k_atlas" / "kaizen" / "runtime_health.py",
    "def check_background_processes() -> dict:",
    "\ndef check_startup_folder() -> dict:",
    runtime_health_func
)

report = {
    "status": "PHASE50B_RUNTIME_PROCESS_COUNT_HARDENED",
    "phase": "50B",
    "changed_files": [
        "k_atlas/kaizen/runtime_control.py",
        "k_atlas/kaizen/runtime_health.py"
    ],
    "goal": "corrigir falso positivo no process_count do runtime local",
    "counting_rule": "contar apenas processo real com -File start_kos_autonomy_scheduler_manual_loop.ps1, excluindo checker e wrapper -Command",
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

out = ROOT / "reports" / "KOS_PHASE50B_RUNTIME_PROCESS_COUNT_HARDENING.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(report, ensure_ascii=False, indent=2))