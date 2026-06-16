from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "briefing"
LATEST_JSON = LOG_DIR / "daily_briefing_latest.json"
LATEST_MD = LOG_DIR / "daily_briefing_latest.md"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _run(cmd: list[str], timeout: int = 30) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[-5000:],
            "stderr": (proc.stderr or "")[-5000:]
        }
    except Exception as exc:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(exc)}

def get_git_summary() -> dict:
    return {
        "branch": _run(["git", "branch", "--show-current"]).get("stdout", "").strip(),
        "status_short": _run(["git", "--no-pager", "status", "--short"]).get("stdout", ""),
        "last_commits": _run(["git", "--no-pager", "log", "--oneline", "-5"]).get("stdout", "")
    }

def _call_summary(module_path: str, fn_name: str) -> dict:
    try:
        module = __import__(module_path, fromlist=[fn_name])
        fn = getattr(module, fn_name)
        return fn()
    except Exception as exc:
        return {"status": "SUMMARY_ERROR", "source": module_path, "error": str(exc)}

def build_operator_briefing(write_log: bool = True) -> dict:
    try:
        from k_atlas.kaizen.runtime_health import build_runtime_health
        health = build_runtime_health(write_log=True)
    except Exception as exc:
        health = {
            "health_status": "ATTENTION_REQUIRED",
            "warnings": [str(exc)],
            "runtime_locks": {
                "production_publish_locked": True,
                "paid_ai_locked": True
            },
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    try:
        from k_atlas.kaizen.self_healing_supervisor import run_self_healing_supervisor
        supervisor = run_self_healing_supervisor(write_log=True)
    except Exception as exc:
        supervisor = {
            "status": "SELF_HEALING_ERROR",
            "error": str(exc),
            "recovery_plan": {"issues": [], "manual_recovery_commands": []},
            "auto_repair_executed": False,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    mission_summary = _call_summary("k_atlas.kaizen.mission_queue", "summarize_queue")
    approval_summary = _call_summary("k_atlas.kaizen.human_approval", "summarize_approvals")
    closed_loop_summary = _call_summary("k_atlas.kaizen.closed_loop", "summarize_last_reports")
    git = get_git_summary()

    warnings = health.get("warnings", []) or []
    issues = supervisor.get("recovery_plan", {}).get("issues", []) or []
    manual_commands = supervisor.get("recovery_plan", {}).get("manual_recovery_commands", []) or []
    git_dirty = bool((git.get("status_short") or "").strip())

    risk_level = "low"
    if warnings or issues or git_dirty:
        risk_level = "medium"
    if any(isinstance(item, dict) and item.get("severity") == "high" for item in issues):
        risk_level = "high"

    priorities = []
    if git_dirty:
        priorities.append("Revisar alteracoes locais antes de novas fases.")
    if warnings:
        priorities.append("Revisar alertas do Runtime Health.")
    if issues:
        priorities.append("Avaliar plano de recuperacao manual do Self-Healing Supervisor.")
    if approval_summary.get("pending", 0):
        priorities.append("Revisar aprovacoes humanas pendentes.")
    if not priorities:
        priorities.append("Sistema saudavel. Proximo passo: evoluir automacao com seguranca.")

    safe_next_commands = [
        {"label": "Health check", "command": "python scripts\\run_phase44_runtime_health_check.py"},
        {"label": "Self-healing supervisor", "command": "python scripts\\run_phase45_self_healing_supervisor.py"},
        {"label": "Git status", "command": "git --no-pager status --short"},
        {"label": "Desligar startup se necessario", "command": "powershell -ExecutionPolicy Bypass -File scripts\\unregister_kos_autonomy_startup_folder.ps1"}
    ]

    summary = {
        "startup_installed": health.get("startup_folder", {}).get("installed"),
        "background_running": health.get("background_processes", {}).get("running"),
        "scheduler_tick_exists": health.get("scheduler_last_tick", {}).get("exists"),
        "git_dirty": git_dirty,
        "mission_total": mission_summary.get("total", 0),
        "approvals_pending": approval_summary.get("pending", 0),
        "production_publish_locked": health.get("runtime_locks", {}).get("production_publish_locked"),
        "paid_ai_locked": health.get("runtime_locks", {}).get("paid_ai_locked")
    }

    briefing = {
        "status": "KOS_OPERATOR_DAILY_BRIEFING_READY",
        "created_at": now(),
        "risk_level": risk_level,
        "health_status": health.get("health_status", "UNKNOWN"),
        "warnings": warnings,
        "issues": issues,
        "manual_recovery_commands": manual_commands,
        "priorities": priorities,
        "safe_next_commands": safe_next_commands,
        "summary": summary,
        "git": git,
        "mission_queue": mission_summary,
        "human_approval": approval_summary,
        "closed_loop": closed_loop_summary,
        "runtime_health": health,
        "self_healing": supervisor,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False
    }

    if write_log:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        _save_json(LATEST_JSON, briefing)
        LATEST_MD.write_text(render_markdown(briefing), encoding="utf-8")

    return briefing

def render_markdown(briefing: dict) -> str:
    summary = briefing.get("summary", {})
    git = briefing.get("git", {})

    lines = [
        "# K-OS Operator Daily Briefing",
        "",
        f"Gerado em: {briefing.get('created_at')}",
        f"Status: {briefing.get('status')}",
        f"Risco: {briefing.get('risk_level')}",
        f"Saude: {briefing.get('health_status')}",
        "",
        "## Snapshot",
        f"- Startup instalado: {summary.get('startup_installed')}",
        f"- Background rodando: {summary.get('background_running')}",
        f"- Scheduler tick existe: {summary.get('scheduler_tick_exists')}",
        f"- Git dirty: {summary.get('git_dirty')}",
        f"- Publicacao producao bloqueada: {summary.get('production_publish_locked')}",
        f"- IA paga bloqueada: {summary.get('paid_ai_locked')}",
        "",
        "## Prioridades"
    ]

    for item in briefing.get("priorities", []):
        lines.append(f"- {item}")

    lines += ["", "## Alertas"]
    if briefing.get("warnings"):
        for item in briefing.get("warnings", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum alerta relevante.")

    lines += ["", "## Issues Self-Healing"]
    if briefing.get("issues"):
        for item in briefing.get("issues", []):
            if isinstance(item, dict):
                lines.append(f"- {item.get('code')}: {item.get('summary')} [{item.get('severity')}]")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("- Nenhuma issue critica.")

    lines += ["", "## Comandos seguros"]
    for item in briefing.get("safe_next_commands", []):
        lines.append(f"- {item.get('label')}: `{item.get('command')}`")

    lines += [
        "",
        "## Git",
        f"Branch: {git.get('branch')}",
        "",
        "```text",
        git.get("status_short") or "workspace limpo",
        "```",
        "",
        "## Ultimos commits",
        "```text",
        git.get("last_commits", ""),
        "```",
        "",
        "## Garantias",
        "- Nenhuma publicacao Instagram executada.",
        "- Nenhuma IA paga chamada.",
        "- Nenhum reparo automatico executado.",
        "- Nenhum segredo exposto."
    ]

    return "\n".join(lines)

if __name__ == "__main__":
    print(json.dumps(build_operator_briefing(write_log=True), ensure_ascii=False, indent=2))
