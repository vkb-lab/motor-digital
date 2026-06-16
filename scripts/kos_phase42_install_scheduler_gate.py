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
    "phase": "42",
    "module": "K-OS Autonomy Scheduler Manual Gate",
    "mode": "MANUAL_LOOP_ONLY",
    "goal": "preparar execucao recorrente local segura sem registrar agendamento automatico",
    "scheduler": {
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "manual_loop_script": "scripts/start_kos_autonomy_scheduler_manual_loop.ps1",
        "one_tick_script": "scripts/run_phase42_scheduler_once.py",
        "default_interval_seconds": 900,
        "default_max_cycles": 1
    },
    "allowed_actions": {
        "run_read_only_snapshot": True,
        "run_safe_executor_dry_run": True,
        "write_local_logs": True,
        "manual_loop": True
    },
    "blocked_actions": {
        "register_windows_task": True,
        "auto_start_24_7": True,
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_access": True,
        "codex_auto_execute": True,
        "production_publish": True
    },
    "hard_rules": {
        "manual_gate_required_for_scheduler_registration": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

scheduler_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "scheduler"
POLICY_PATH = ROOT / "config" / "kos_autonomy_scheduler_policy.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def build_scheduler_plan() -> dict:
    policy = _read_json(POLICY_PATH, {})
    scheduler = policy.get("scheduler", {})

    return {
        "status": "SCHEDULER_MANUAL_GATE_READY",
        "mode": policy.get("mode", "MANUAL_LOOP_ONLY"),
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "manual_loop_script": scheduler.get("manual_loop_script", "scripts/start_kos_autonomy_scheduler_manual_loop.ps1"),
        "one_tick_script": scheduler.get("one_tick_script", "scripts/run_phase42_scheduler_once.py"),
        "default_interval_seconds": scheduler.get("default_interval_seconds", 900),
        "default_max_cycles": scheduler.get("default_max_cycles", 1),
        "next_phase_required_for_windows_task": "PHASE_43_EXPLICIT_WINDOWS_TASK_REGISTRATION",
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

def run_scheduler_tick(cycle_id: str | None = None) -> dict:
    cycle_id = cycle_id or "scheduler_tick"

    try:
        from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot
        snapshot = build_autonomy_snapshot(write_log=True)
    except Exception as exc:
        snapshot = {
            "status": "SNAPSHOT_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    try:
        from k_atlas.kaizen.safe_executor import run_safe_bundle
        safe_check = run_safe_bundle(
            bundle_id=f"{cycle_id}_dry_run",
            actions=["git_branch", "git_status"],
            dry_run=True,
        )
    except Exception as exc:
        safe_check = {
            "status": "SAFE_EXECUTOR_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    report = {
        "status": "SCHEDULER_TICK_COMPLETED",
        "cycle_id": cycle_id,
        "mode": "MANUAL_LOOP_ONLY",
        "snapshot": snapshot,
        "safe_check": safe_check,
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _save_json(LOG_DIR / "last_tick.json", report)

    return report

def summarize_scheduler() -> dict:
    last_tick = _read_json(LOG_DIR / "last_tick.json", {})
    return {
        "status": "SCHEDULER_SUMMARY",
        "plan": build_scheduler_plan(),
        "last_tick": last_tick,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }

if __name__ == "__main__":
    print(json.dumps(run_scheduler_tick("phase42_smoke"), ensure_ascii=False, indent=2))
'''

runner_code = r'''
from k_atlas.kaizen.scheduler_gate import run_scheduler_tick, build_scheduler_plan
import json

if __name__ == "__main__":
    result = run_scheduler_tick("phase42_manual_tick")

    print(json.dumps({
        "status": "PHASE42_SCHEDULER_TICK_COMPLETED",
        "tick_status": result.get("status"),
        "scheduler_plan": build_scheduler_plan(),
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

manual_loop_ps1 = r'''
$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"

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
Write-Host "[KOS] Intervalo segundos:" $interval
Write-Host "[KOS] Max cycles:" $max
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."

while($true){
  $count += 1
  Write-Host "[KOS] Scheduler tick:" $count
  python scripts\run_phase42_scheduler_once.py

  if($max -gt 0 -and $count -ge $max){
    Write-Host "[KOS] Scheduler manual loop finalizado por max cycles."
    break
  }

  Start-Sleep -Seconds $interval
}
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.scheduler_gate import summarize_scheduler, run_scheduler_tick

st.set_page_config(page_title="KOS Scheduler Gate", layout="wide")

st.title("KOS Autonomy Scheduler Manual Gate")
st.caption("Preparacao para recorrencia local. Nao registra tarefa Windows e nao liga 24/7 automaticamente.")

summary = summarize_scheduler()
plan = summary.get("plan", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Mode", plan.get("mode", "N/A"))
col2.metric("Windows task", "ON" if plan.get("windows_task_registered") else "OFF")
col3.metric("Auto start", "ON" if plan.get("auto_start_enabled") else "OFF")
col4.metric("Interval", plan.get("default_interval_seconds", 900))

st.subheader("Plano de scheduler")
st.json(plan)

st.subheader("Rodar um tick manual seguro")
if st.button("Rodar tick manual", use_container_width=True):
    result = run_scheduler_tick("streamlit_manual_tick")
    st.json(result)

st.subheader("Ultimo tick")
st.json(summary.get("last_tick", {}))

st.warning("Esta fase nao registra agendamento automatico. A Fase 43 exige confirmacao explicita.")
'''

test_code = r'''
from k_atlas.kaizen.scheduler_gate import build_scheduler_plan, run_scheduler_tick, summarize_scheduler

def test_scheduler_plan_is_manual_only():
    plan = build_scheduler_plan()

    assert plan["status"] == "SCHEDULER_MANUAL_GATE_READY"
    assert plan["windows_task_registered"] is False
    assert plan["auto_start_enabled"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_scheduler_tick_is_safe():
    result = run_scheduler_tick("test_phase42")

    assert result["status"] == "SCHEDULER_TICK_COMPLETED"
    assert result["windows_task_registered"] is False
    assert result["auto_start_enabled"] is False
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
    assert result["external_side_effects_executed"] is False

def test_scheduler_summary_safe():
    summary = summarize_scheduler()

    assert summary["status"] == "SCHEDULER_SUMMARY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_autonomy_scheduler_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "scheduler_gate.py", scheduler_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase42_scheduler_once.py", runner_code.strip() + "\n")
write(ROOT / "scripts" / "start_kos_autonomy_scheduler_manual_loop.ps1", manual_loop_ps1.strip() + "\n")
write(ROOT / "pages" / "KOS_Scheduler_Gate.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase42_scheduler_gate.py", test_code.strip() + "\n")

report = {
    "status": "PHASE42_AUTONOMY_SCHEDULER_GATE_BOOTSTRAPPED",
    "phase": "42",
    "created_files": [
        "config/kos_autonomy_scheduler_policy.json",
        "k_atlas/kaizen/scheduler_gate.py",
        "scripts/run_phase42_scheduler_once.py",
        "scripts/start_kos_autonomy_scheduler_manual_loop.ps1",
        "pages/KOS_Scheduler_Gate.py",
        "tests/test_phase42_scheduler_gate.py"
    ],
    "runtime_files": [
        "logs/kaizen/scheduler/last_tick.json"
    ],
    "windows_task_registered": False,
    "auto_start_enabled": False,
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE42_AUTONOMY_SCHEDULER_GATE_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))