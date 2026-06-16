from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]

BRIDGE_INBOX = ROOT / "local_runtime" / "operator_command_bridge" / "inbox"
COWORKER_DIR = ROOT / "local_runtime" / "kos_local_coworker"
TASKS_DIR = COWORKER_DIR / "tasks"
LOGS_DIR = COWORKER_DIR / "logs"
STATE_PATH = COWORKER_DIR / "state.json"
LATEST_STATUS = COWORKER_DIR / "latest_status.json"
EVENTS_PATH = LOGS_DIR / "events.jsonl"

SAFE_DIAGNOSTIC_COMMANDS = {
    "git_status": "git --no-pager status --short",
    "git_log": "git --no-pager log --oneline -5",
    "runtime_status": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status",
}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_state() -> dict:
    state = _read_json(STATE_PATH)
    if not state:
        state = {
            "status": "KOS_LOCAL_COWORKER_STATE_READY",
            "processed_command_ids": [],
            "created_at": now(),
            "updated_at": now(),
        }
    return state

def save_state(state: dict) -> None:
    state["updated_at"] = now()
    _write_json(STATE_PATH, state)

def detect_ollama() -> dict:
    try:
        result = subprocess.run(
            "ollama --version",
            cwd=ROOT,
            shell=True,
            text=True,
            capture_output=True,
            timeout=5,
        )
        output = (result.stdout or result.stderr or "").strip()
        return {
            "available": result.returncode == 0,
            "status": "OLLAMA_AVAILABLE" if result.returncode == 0 else "OLLAMA_NOT_AVAILABLE",
            "output": output[:500],
            "paid_ai_used": False,
        }
    except Exception as exc:
        return {
            "available": False,
            "status": "OLLAMA_CHECK_FAILED",
            "error": str(exc),
            "paid_ai_used": False,
        }

def run_safe_diagnostics() -> dict:
    results = {}
    for key, command in SAFE_DIAGNOSTIC_COMMANDS.items():
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                shell=True,
                text=True,
                capture_output=True,
                timeout=20,
            )
            results[key] = {
                "command": command,
                "returncode": result.returncode,
                "stdout": (result.stdout or "").strip()[-3000:],
                "stderr": (result.stderr or "").strip()[-3000:],
                "executed": True,
                "safe_allowlisted": True,
            }
        except Exception as exc:
            results[key] = {
                "command": command,
                "error": str(exc),
                "executed": False,
                "safe_allowlisted": True,
            }

    return {
        "status": "KOS_LOCAL_COWORKER_DIAGNOSTICS_READY",
        "results": results,
        "arbitrary_shell_executed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

def classify_command(command: dict) -> dict:
    title = str(command.get("title", "")).lower()
    body = str(command.get("body", "")).lower()
    area = str(command.get("area", "")).lower()
    text = f"{title}\n{body}\n{area}"

    task_type = "general_operation"
    if "fase" in text or "phase" in text:
        task_type = "phase_execution_plan"
    if "qa" in text or "quality" in text:
        task_type = "qa_operation"
    if "certifica" in text or "baseline" in text or "tag" in text:
        task_type = "certification_operation"
    if "export" in text or "packager" in text:
        task_type = "export_packager_operation"
    if "ollama" in text or "coworker" in text or "autonomia" in text:
        task_type = "local_autonomy_operation"

    risk = "low"
    risk_reasons = []

    for term in ["deploy", "instagram", "meta", "token", "secret", "senha", "credential", ".env", "push", "tag"]:
        if term in text:
            risk = "medium"
            risk_reasons.append(f"contains_{term}")

    for term in ["publicar", "production", "delete", "deletar", "remove", "remover", "segredo"]:
        if term in text:
            risk = "high"
            risk_reasons.append(f"contains_{term}")

    return {
        "task_type": task_type,
        "risk": risk,
        "risk_reasons": risk_reasons,
        "ask_k_atlas_engineer": risk in {"medium", "high"},
    }

def build_task_from_command(command: dict, ollama_status: dict | None = None, diagnostics: dict | None = None) -> dict:
    command_id = command.get("command_id") or "MANUAL-" + uuid.uuid4().hex[:10].upper()
    classification = classify_command(command)
    task_id = "KOS-COWORKER-" + uuid.uuid4().hex[:12].upper()

    task = {
        "status": "KOS_LOCAL_COWORKER_TASK_READY",
        "task_id": task_id,
        "source_command_id": command_id,
        "title": command.get("title") or "Comando sem titulo",
        "priority": command.get("priority") or "normal",
        "area": command.get("area") or "general",
        "body": command.get("body") or "",
        "classification": classification,
        "autonomy": {
            "tier": "TIER_1_PLAN_AND_DIAGNOSTICS",
            "can_read_command_bridge": True,
            "can_create_task_capsule": True,
            "can_run_safe_diagnostics": True,
            "can_use_ollama_if_available": True,
            "can_write_repo_files": False,
            "can_execute_arbitrary_shell": False,
            "can_commit": False,
            "can_push": False,
            "can_deploy": False,
            "can_publish_instagram": False,
            "can_use_paid_ai": False,
        },
        "safe_plan": [
            {
                "step": "diagnose",
                "description": "Verificar Git, runtime e disponibilidade local.",
                "allowed_now": True,
            },
            {
                "step": "prepare",
                "description": "Converter comando em tarefa local auditavel.",
                "allowed_now": True,
            },
            {
                "step": "propose",
                "description": "Preparar proximo comando para operador revisar.",
                "allowed_now": True,
            },
            {
                "step": "execute_repo_change",
                "description": "Alterar arquivos do repositorio somente com comando explicito do operador.",
                "allowed_now": False,
            },
        ],
        "recommended_next_action": "Consultar K-Atlas Engineer na conversa aberta antes de alterar codigo." if classification.get("ask_k_atlas_engineer") else "Pode preparar plano local sem executar alteracoes no repositorio.",
        "ollama_status": ollama_status or detect_ollama(),
        "diagnostics": diagnostics or {},
        "gates": {
            "repo_write_allowed": False,
            "arbitrary_shell_allowed": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    return task

def load_bridge_commands(limit: int = 20) -> list[dict]:
    if not BRIDGE_INBOX.exists():
        return []

    commands = []
    paths = sorted(BRIDGE_INBOX.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]

    for path in paths:
        payload = _read_json(path)
        if payload:
            payload["_source_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            commands.append(payload)

    return commands

def save_task(task: dict) -> dict:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    path = TASKS_DIR / f"{task['task_id']}.json"
    _write_json(path, task)

    event = {
        "status": "KOS_LOCAL_COWORKER_TASK_SAVED",
        "task_id": task.get("task_id"),
        "source_command_id": task.get("source_command_id"),
        "title": task.get("title"),
        "risk": task.get("classification", {}).get("risk"),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "created_at": now(),
        "real_action_executed": False,
    }
    _append_jsonl(EVENTS_PATH, event)
    return event

def process_bridge_inbox(limit: int = 5, execute_diagnostics: bool = True) -> dict:
    state = load_state()
    processed = set(state.get("processed_command_ids", []))

    commands = load_bridge_commands(limit=50)
    pending = [item for item in commands if item.get("command_id") not in processed]

    ollama_status = detect_ollama()
    diagnostics = run_safe_diagnostics() if execute_diagnostics else {}

    created_tasks = []

    for command in pending[:limit]:
        task = build_task_from_command(command, ollama_status=ollama_status, diagnostics=diagnostics)
        saved = save_task(task)
        created_tasks.append({
            "task_id": task.get("task_id"),
            "source_command_id": task.get("source_command_id"),
            "title": task.get("title"),
            "risk": task.get("classification", {}).get("risk"),
            "task_type": task.get("classification", {}).get("task_type"),
            "saved": saved,
        })
        processed.add(command.get("command_id"))

    state["processed_command_ids"] = sorted(processed)
    state["last_run_at"] = now()
    state["last_created_tasks_count"] = len(created_tasks)
    save_state(state)

    status = {
        "status": "KOS_LOCAL_COWORKER_TICK_COMPLETED",
        "commands_seen": len(commands),
        "pending_commands_before_tick": len(pending),
        "created_tasks_count": len(created_tasks),
        "created_tasks": created_tasks,
        "ollama_status": ollama_status,
        "diagnostics_executed": execute_diagnostics,
        "diagnostics": diagnostics,
        "gates": {
            "repo_write_allowed": False,
            "arbitrary_shell_allowed": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    _write_json(LATEST_STATUS, status)
    _append_jsonl(EVENTS_PATH, status)
    return status

def get_latest_status() -> dict:
    if LATEST_STATUS.exists():
        return _read_json(LATEST_STATUS)
    return process_bridge_inbox(limit=1, execute_diagnostics=False)

if __name__ == "__main__":
    print(json.dumps(process_bridge_inbox(), ensure_ascii=False, indent=2))