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
    "phase": "45",
    "module": "K-OS Self-Healing Local Supervisor",
    "mode": "DIAGNOSE_AND_RECOMMEND_ONLY",
    "goal": "detectar falhas locais do K-OS 24/7 e gerar plano de recuperacao manual seguro",
    "allowed_actions": {
        "read_runtime_health": True,
        "detect_failures": True,
        "generate_recovery_plan": True,
        "write_local_report": True,
        "show_manual_commands": True
    },
    "blocked_actions": {
        "auto_repair": True,
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "git_reset_auto": True
    },
    "hard_rules": {
        "diagnose_only": True,
        "manual_confirmation_required_for_repair": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

supervisor_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "self_healing"
LAST_REPORT = LOG_DIR / "last_supervisor_report.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _safe_command(command: str, reason: str, risk: str = "low") -> dict:
    return {
        "command": command,
        "reason": reason,
        "risk": risk,
        "requires_human_execution": True,
        "auto_executed": False,
    }

def build_recovery_plan(health: dict) -> dict:
    warnings = health.get("warnings", []) or []
    startup = health.get("startup_folder", {}) or {}
    processes = health.get("background_processes", {}) or {}
    tick = health.get("scheduler_last_tick", {}) or {}
    git = health.get("git", {}) or {}
    locks = health.get("runtime_locks", {}) or {}

    issues = []
    commands = []

    if not startup.get("installed"):
        issues.append({
            "code": "STARTUP_NOT_INSTALLED",
            "severity": "medium",
            "summary": "Startup Folder nao esta instalado."
        })
        commands.append(_safe_command(
            'powershell -ExecutionPolicy Bypass -File scripts\\register_kos_autonomy_startup_folder.ps1',
            "Registrar o K-OS no Startup Folder com confirmacao humana exata.",
            "medium"
        ))

    if not processes.get("running"):
        issues.append({
            "code": "BACKGROUND_LOOP_NOT_RUNNING",
            "severity": "medium",
            "summary": "Loop local em background nao foi detectado."
        })
        commands.append(_safe_command(
            '$ErrorActionPreference="Stop"; Set-Location "C:\\Users\\oi\\Desktop\\motor-digital"; $env:KOS_SCHEDULER_INTERVAL_SECONDS="900"; $env:KOS_SCHEDULER_MAX_CYCLES="0"; powershell -ExecutionPolicy Bypass -File scripts\\start_kos_autonomy_scheduler_manual_loop.ps1',
            "Iniciar o loop manualmente na sessao atual.",
            "medium"
        ))

    if not tick.get("exists"):
        issues.append({
            "code": "SCHEDULER_TICK_MISSING",
            "severity": "low",
            "summary": "Arquivo do ultimo tick ainda nao existe."
        })
        commands.append(_safe_command(
            'python scripts\\run_phase42_scheduler_once.py',
            "Gerar um tick seguro para validar o scheduler.",
            "low"
        ))

    if bool((git.get("status_short") or "").strip()):
        issues.append({
            "code": "GIT_DIRTY",
            "severity": "medium",
            "summary": "Repositorio possui alteracoes locais."
        })
        commands.append(_safe_command(
            'git --no-pager status --short',
            "Inspecionar alteracoes locais antes de qualquer nova fase.",
            "low"
        ))

    if not locks.get("production_publish_locked", True):
        issues.append({
            "code": "PRODUCTION_PUBLISH_UNLOCKED",
            "severity": "high",
            "summary": "Flag de publicacao real parece habilitada."
        })
        commands.append(_safe_command(
            'Get-Content local_runtime\\ig_runtime.env -Encoding UTF8',
            "Revisar runtime local e bloquear publicacao real antes de continuar.",
            "high"
        ))

    if not locks.get("paid_ai_locked", True):
        issues.append({
            "code": "PAID_AI_UNLOCKED",
            "severity": "high",
            "summary": "IA paga parece habilitada."
        })
        commands.append(_safe_command(
            'Get-Content local_runtime\\ai_runtime.env -Encoding UTF8',
            "Revisar runtime local e bloquear IA paga antes de continuar.",
            "high"
        ))

    if not issues and not warnings:
        status = "SELF_HEALING_SUPERVISOR_HEALTHY"
        recommendation = "Nenhum reparo necessario agora."
    else:
        status = "SELF_HEALING_SUPERVISOR_ATTENTION_REQUIRED"
        recommendation = "Executar apenas comandos manuais sugeridos, se fizer sentido."

    return {
        "status": status,
        "issues": issues,
        "warnings": warnings,
        "manual_recovery_commands": commands,
        "recommendation": recommendation,
        "auto_repair_executed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

def run_self_healing_supervisor(write_log: bool = True) -> dict:
    try:
        from k_atlas.kaizen.runtime_health import build_runtime_health
        health = build_runtime_health(write_log=True)
    except Exception as exc:
        health = {
            "status": "RUNTIME_HEALTH_ERROR",
            "health_status": "ATTENTION_REQUIRED",
            "warnings": [str(exc)],
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    plan = build_recovery_plan(health)

    report = {
        "status": plan["status"],
        "mode": "DIAGNOSE_AND_RECOMMEND_ONLY",
        "health": health,
        "recovery_plan": plan,
        "auto_repair_executed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    if write_log:
        _save_json(LAST_REPORT, report)

    return report

if __name__ == "__main__":
    print(json.dumps(run_self_healing_supervisor(write_log=True), ensure_ascii=False, indent=2))
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.self_healing_supervisor import run_self_healing_supervisor

if __name__ == "__main__":
    result = run_self_healing_supervisor(write_log=True)
    plan = result.get("recovery_plan", {})

    print(json.dumps({
        "status": "PHASE45_SELF_HEALING_SUPERVISOR_COMPLETED",
        "supervisor_status": result.get("status"),
        "issues_count": len(plan.get("issues", [])),
        "warnings": plan.get("warnings", []),
        "manual_commands_count": len(plan.get("manual_recovery_commands", [])),
        "auto_repair_executed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.self_healing_supervisor import run_self_healing_supervisor

st.set_page_config(page_title="KOS Self-Healing Supervisor", layout="wide")

st.title("KOS Self-Healing Local Supervisor")
st.caption("Diagnostica falhas locais e sugere reparos manuais. Nao executa reparos automaticamente.")

report = run_self_healing_supervisor(write_log=True)
plan = report.get("recovery_plan", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Supervisor", report.get("status", "N/A"))
col2.metric("Issues", len(plan.get("issues", [])))
col3.metric("Commands", len(plan.get("manual_recovery_commands", [])))
col4.metric("Auto repair", "NAO")

if plan.get("issues"):
    st.warning(plan.get("issues"))
else:
    st.success("Nenhum problema critico detectado.")

st.subheader("Comandos manuais sugeridos")
for item in plan.get("manual_recovery_commands", []):
    st.code(item.get("command", ""))
    st.caption(item.get("reason", ""))

st.subheader("Relatorio completo")
st.json(report)

st.warning("Supervisor read-only. Nao publica, nao usa IA paga e nao executa reparo automatico.")
'''

test_code = r'''
from k_atlas.kaizen.self_healing_supervisor import build_recovery_plan, run_self_healing_supervisor

def test_recovery_plan_is_diagnose_only_when_healthy():
    health = {
        "warnings": [],
        "startup_folder": {"installed": True},
        "background_processes": {"running": True},
        "scheduler_last_tick": {"exists": True},
        "git": {"status_short": ""},
        "runtime_locks": {
            "production_publish_locked": True,
            "paid_ai_locked": True,
        },
    }

    plan = build_recovery_plan(health)

    assert plan["status"] == "SELF_HEALING_SUPERVISOR_HEALTHY"
    assert plan["auto_repair_executed"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_recovery_plan_suggests_manual_commands():
    health = {
        "warnings": ["Loop em background nao detectado agora."],
        "startup_folder": {"installed": False},
        "background_processes": {"running": False},
        "scheduler_last_tick": {"exists": False},
        "git": {"status_short": " M example.txt"},
        "runtime_locks": {
            "production_publish_locked": True,
            "paid_ai_locked": True,
        },
    }

    plan = build_recovery_plan(health)

    assert plan["status"] == "SELF_HEALING_SUPERVISOR_ATTENTION_REQUIRED"
    assert len(plan["issues"]) >= 1
    assert len(plan["manual_recovery_commands"]) >= 1
    assert all(cmd["auto_executed"] is False for cmd in plan["manual_recovery_commands"])

def test_supervisor_never_executes_repair():
    report = run_self_healing_supervisor(write_log=False)

    assert report["auto_repair_executed"] is False
    assert report["real_action_executed"] is False
    assert report["paid_ai_call_executed"] is False
    assert report["instagram_publish_executed"] is False
    assert report["external_side_effects_executed"] is False
'''

save_json(ROOT / "config" / "kos_self_healing_supervisor_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "self_healing_supervisor.py", supervisor_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase45_self_healing_supervisor.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Self_Healing_Supervisor.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase45_self_healing_supervisor.py", test_code.strip() + "\n")

report = {
    "status": "PHASE45_SELF_HEALING_SUPERVISOR_BOOTSTRAPPED",
    "phase": "45",
    "created_files": [
        "config/kos_self_healing_supervisor_policy.json",
        "k_atlas/kaizen/self_healing_supervisor.py",
        "scripts/run_phase45_self_healing_supervisor.py",
        "pages/KOS_Self_Healing_Supervisor.py",
        "tests/test_phase45_self_healing_supervisor.py"
    ],
    "runtime_files": [
        "logs/kaizen/self_healing/last_supervisor_report.json"
    ],
    "auto_repair_executed": False,
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE45_SELF_HEALING_SUPERVISOR_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))