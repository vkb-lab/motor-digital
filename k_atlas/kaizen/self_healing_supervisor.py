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
