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
    "phase": "47",
    "module": "K-OS Briefing Scheduler Integration",
    "mode": "LOCAL_RECURRING_READ_ONLY",
    "goal": "integrar briefing operacional ao ciclo recorrente local do K-OS",
    "allowed_actions": {
        "run_scheduler_tick": True,
        "run_operator_briefing": True,
        "write_local_runtime_logs": True,
        "read_git_status": True,
        "read_runtime_health": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "auto_commit": True,
        "auto_push": True
    },
    "hard_rules": {
        "read_only_runtime": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

briefing_scheduler_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "briefing_scheduler"
LAST_TICK = LOG_DIR / "last_briefing_scheduler_tick.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def run_briefing_scheduler_tick(cycle_id: str = "briefing_scheduler_tick") -> dict:
    try:
        from k_atlas.kaizen.scheduler_gate import run_scheduler_tick
        scheduler_result = run_scheduler_tick(cycle_id=cycle_id)
    except Exception as exc:
        scheduler_result = {
            "status": "SCHEDULER_TICK_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    try:
        from k_atlas.kaizen.operator_briefing import build_operator_briefing
        briefing = build_operator_briefing(write_log=True)
    except Exception as exc:
        briefing = {
            "status": "OPERATOR_BRIEFING_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    report = {
        "status": "BRIEFING_SCHEDULER_TICK_COMPLETED",
        "cycle_id": cycle_id,
        "scheduler_result": scheduler_result,
        "operator_briefing": {
            "status": briefing.get("status"),
            "risk_level": briefing.get("risk_level"),
            "health_status": briefing.get("health_status"),
            "priorities": briefing.get("priorities", []),
            "summary": briefing.get("summary", {}),
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    _save_json(LAST_TICK, report)
    return report

def summarize_briefing_scheduler() -> dict:
    if LAST_TICK.exists():
        try:
            last_tick = json.loads(LAST_TICK.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            last_tick = {"error": str(exc)}
    else:
        last_tick = {}

    return {
        "status": "BRIEFING_SCHEDULER_SUMMARY",
        "last_tick_exists": LAST_TICK.exists(),
        "last_tick_path": str(LAST_TICK.relative_to(ROOT)).replace("\\", "/"),
        "last_tick": last_tick,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }

if __name__ == "__main__":
    print(json.dumps(run_briefing_scheduler_tick("phase47_smoke"), ensure_ascii=False, indent=2))
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.briefing_scheduler import run_briefing_scheduler_tick, summarize_briefing_scheduler

if __name__ == "__main__":
    result = run_briefing_scheduler_tick("phase47_manual_tick")
    print(json.dumps({
        "status": "PHASE47_BRIEFING_SCHEDULER_TICK_COMPLETED",
        "tick_status": result.get("status"),
        "briefing_status": result.get("operator_briefing", {}).get("status"),
        "risk_level": result.get("operator_briefing", {}).get("risk_level"),
        "summary": summarize_briefing_scheduler(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

manual_loop_ps1 = r'''
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
Write-Host "[KOS] Modo: scheduler + briefing operacional."
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."

while($true){
  $count += 1
  Write-Host "[KOS] Scheduler briefing tick:" $count
  python scripts\run_phase47_briefing_scheduler_tick.py

  if($LASTEXITCODE -ne 0){
    throw "Scheduler briefing tick falhou."
  }

  if($max -gt 0 -and $count -ge $max){
    Write-Host "[KOS] Scheduler manual loop finalizado por max cycles."
    break
  }

  Start-Sleep -Seconds $interval
}
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.briefing_scheduler import run_briefing_scheduler_tick, summarize_briefing_scheduler

st.set_page_config(page_title="KOS Briefing Scheduler", layout="wide")

st.title("KOS Briefing Scheduler")
st.caption("Integra scheduler local com briefing operacional read-only.")

summary = summarize_briefing_scheduler()
last_tick = summary.get("last_tick", {})

col1, col2, col3 = st.columns(3)
col1.metric("Last tick exists", "SIM" if summary.get("last_tick_exists") else "NAO")
col2.metric("Tick status", last_tick.get("status", "N/A"))
col3.metric("External actions", "NAO")

if st.button("Rodar tick com briefing agora", use_container_width=True):
    result = run_briefing_scheduler_tick("streamlit_phase47_tick")
    st.json(result)

st.subheader("Resumo")
st.json(summary)

st.warning("Read-only. Nao publica, nao usa IA paga, nao executa Codex e nao commita automaticamente.")
'''

test_code = r'''
from k_atlas.kaizen.briefing_scheduler import run_briefing_scheduler_tick, summarize_briefing_scheduler

def test_briefing_scheduler_tick_is_safe():
    result = run_briefing_scheduler_tick("test_phase47")

    assert result["status"] == "BRIEFING_SCHEDULER_TICK_COMPLETED"
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
    assert result["external_side_effects_executed"] is False

def test_briefing_scheduler_summary_is_safe():
    summary = summarize_briefing_scheduler()

    assert summary["status"] == "BRIEFING_SCHEDULER_SUMMARY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_briefing_scheduler_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "briefing_scheduler.py", briefing_scheduler_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase47_briefing_scheduler_tick.py", runner_code.strip() + "\n")
write(ROOT / "scripts" / "start_kos_autonomy_scheduler_manual_loop.ps1", manual_loop_ps1.strip() + "\n")
write(ROOT / "pages" / "KOS_Briefing_Scheduler.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase47_briefing_scheduler.py", test_code.strip() + "\n")

report = {
    "status": "PHASE47_BRIEFING_SCHEDULER_BOOTSTRAPPED",
    "phase": "47",
    "created_files": [
        "config/kos_briefing_scheduler_policy.json",
        "k_atlas/kaizen/briefing_scheduler.py",
        "scripts/run_phase47_briefing_scheduler_tick.py",
        "scripts/start_kos_autonomy_scheduler_manual_loop.ps1",
        "pages/KOS_Briefing_Scheduler.py",
        "tests/test_phase47_briefing_scheduler.py"
    ],
    "runtime_files": [
        "logs/kaizen/briefing_scheduler/last_briefing_scheduler_tick.json",
        "logs/kaizen/briefing/daily_briefing_latest.json",
        "logs/kaizen/briefing/daily_briefing_latest.md"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE47_BRIEFING_SCHEDULER_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))