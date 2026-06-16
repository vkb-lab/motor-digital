from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

PREAMBLE = '''from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

'''

runner_files = [
    "scripts/run_phase36_planner_bridge.py",
    "scripts/run_phase37_mission_queue_demo.py",
    "scripts/run_phase38_safe_executor_demo.py",
    "scripts/run_phase39_human_approval_demo.py",
    "scripts/run_phase40_closed_loop_demo.py",
    "scripts/run_phase41_autonomy_dashboard_snapshot.py",
    "scripts/run_phase42_scheduler_once.py",
    "scripts/run_phase43_windows_task_gate_check.py",
]

patched = []

for rel in runner_files:
    path = ROOT / rel
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8-sig")

    if "sys.path.insert(0, str(ROOT))" not in text:
        path.write_text(PREAMBLE + text, encoding="utf-8")
        patched.append(rel)

manual_loop = ROOT / "scripts/start_kos_autonomy_scheduler_manual_loop.ps1"

manual_loop.write_text(r'''
$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

if(!$env:KOS_SCHEDULER_INTERVAL_SECONDS){
  $env:KOS_SCHEDULER_INTERVAL_SECONDS="900"
}

if(!$env:KOS_SCHEDULER_MAX_CYCLES){
  $env:KOS_SCHEDULER_MAX_CYCLES="1"
}

$interval=[int]$env:KOS_SCHEDULER_INTERVAL_SECONDS
$max=[int]$env:KOS_SCHEDULER_MAX_CYCLES
$count=0

Write-Host "[KOS] Scheduler manual loop iniciado."
Write-Host "[KOS] Project root:" $ProjectRoot
Write-Host "[KOS] PYTHONPATH:" $env:PYTHONPATH
Write-Host "[KOS] Intervalo segundos:" $interval
Write-Host "[KOS] Max cycles:" $max
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."

while($true){
  $count += 1
  Write-Host "[KOS] Scheduler tick:" $count
  python scripts\run_phase42_scheduler_once.py

  if($LASTEXITCODE -ne 0){
    throw "Scheduler tick falhou."
  }

  if($max -gt 0 -and $count -ge $max){
    Write-Host "[KOS] Scheduler manual loop finalizado por max cycles."
    break
  }

  Start-Sleep -Seconds $interval
}
'''.strip() + "\n", encoding="utf-8")

patched.append("scripts/start_kos_autonomy_scheduler_manual_loop.ps1")

report = {
    "status": "PHASE43C_PYTHONPATH_HARDENED",
    "phase": "43C",
    "patched_files": patched,
    "task_registered": False,
    "auto_start_enabled": False,
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

(ROOT / "reports/KOS_PHASE43C_PYTHONPATH_HARDENING_REPORT.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False, indent=2))