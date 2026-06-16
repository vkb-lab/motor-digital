from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]

WORK_ORDERS_DIR = ROOT / "local_runtime" / "kos_local_patch_workspace" / "work_orders"
COMPOSER_DIR = ROOT / "local_runtime" / "kos_local_command_composer"
COMMANDS_DIR = COMPOSER_DIR / "commands"
LOGS_DIR = COMPOSER_DIR / "logs"
LATEST_STATUS = COMPOSER_DIR / "latest_command_composer_status.json"
EVENTS_PATH = LOGS_DIR / "events.jsonl"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_work_orders(limit: int = 20) -> list[dict]:
    if not WORK_ORDERS_DIR.exists():
        return []

    paths = sorted(WORK_ORDERS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    items = []

    for path in paths:
        item = _read_json(path)
        if item:
            item["_source_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            items.append(item)

    return items

def load_existing_command_drafts(limit: int = 200) -> list[dict]:
    if not COMMANDS_DIR.exists():
        return []

    paths = sorted(COMMANDS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    items = []

    for path in paths:
        item = _read_json(path)
        if item:
            items.append(item)

    return items

def _ps_array(items: list[str]) -> str:
    if not items:
        return "@()"
    quoted = [f'"{item}"' for item in items]
    return "@(" + ",".join(quoted) + ")"

def build_command_draft_from_work_order(work_order: dict) -> dict:
    draft_id = "KOS-CMD-DRAFT-" + uuid.uuid4().hex[:12].upper()

    files = work_order.get("proposed_repo_files", []) or []
    file_paths = [item.get("path") for item in files if item.get("path")]

    title = work_order.get("title") or "K-OS Work Order"
    risk = work_order.get("risk") or "unknown"
    work_order_id = work_order.get("work_order_id") or "unknown"

    command = f'''$ErrorActionPreference="Stop";
Set-Location "C:\\Users\\oi\\Desktop\\motor-digital";

Write-Host "[KOS] Command draft gerado pelo Local Command Composer.";
Write-Host "[KOS] Work order: {work_order_id}";
Write-Host "[KOS] Titulo: {title}";
Write-Host "[KOS] Risco: {risk}";
Write-Host "[KOS] Este comando NAO aplica alteracoes automaticamente.";

Write-Host "[KOS] Diagnostico inicial:";
git --no-pager status --short;
powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status;

$ProposedFiles = {_ps_array(file_paths)};

Write-Host "[KOS] Arquivos propostos pela work order:";
foreach($f in $ProposedFiles){{
  Write-Host " - $f";
}}

Write-Host "[KOS] Proximo passo:";
Write-Host "Enviar esta work order ao K-Atlas Engineer para gerar comando de implementacao completo.";

Write-Host "[KOS] Gates:";
Write-Host "repo_write_allowed_now=false";
Write-Host "patch_apply_allowed_now=false";
Write-Host "commit_allowed=false";
Write-Host "push_allowed=false";
Write-Host "deploy_allowed=false";
Write-Host "paid_ai_allowed=false";
Write-Host "instagram_publish_allowed=false";
'''

    draft = {
        "status": "KOS_LOCAL_COMMAND_DRAFT_READY",
        "draft_id": draft_id,
        "source_work_order_id": work_order_id,
        "source_task_id": work_order.get("source_task_id"),
        "source_command_id": work_order.get("source_command_id"),
        "title": title,
        "risk": risk,
        "task_type": work_order.get("task_type"),
        "proposed_repo_files": files,
        "powershell_command": command,
        "gates": {
            "execute_allowed_now": False,
            "repo_write_allowed_now": False,
            "patch_apply_allowed_now": False,
            "arbitrary_shell_allowed": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
            "ask_k_atlas_engineer": True
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    return draft

def save_command_draft(draft: dict) -> dict:
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    base = draft["draft_id"]
    json_path = COMMANDS_DIR / f"{base}.json"
    ps1_path = COMMANDS_DIR / f"{base}.ps1"
    md_path = COMMANDS_DIR / f"{base}.md"

    _write_json(json_path, draft)
    _write_text(ps1_path, draft["powershell_command"])

    md = "\n".join([
        f"# {draft.get('title')}",
        "",
        f"- Draft: {draft.get('draft_id')}",
        f"- Work order: {draft.get('source_work_order_id')}",
        f"- Risco: {draft.get('risk')}",
        "",
        "## Comando PowerShell",
        "",
        "```powershell",
        draft.get("powershell_command", ""),
        "```",
        "",
        "## Gates",
        "",
        "- execute_allowed_now: false",
        "- repo_write_allowed_now: false",
        "- patch_apply_allowed_now: false",
        "- human_review_required: true",
        ""
    ])
    _write_text(md_path, md)

    event = {
        "status": "KOS_LOCAL_COMMAND_DRAFT_SAVED",
        "draft_id": draft.get("draft_id"),
        "source_work_order_id": draft.get("source_work_order_id"),
        "title": draft.get("title"),
        "risk": draft.get("risk"),
        "json_path": str(json_path.relative_to(ROOT)).replace("\\", "/"),
        "ps1_path": str(ps1_path.relative_to(ROOT)).replace("\\", "/"),
        "md_path": str(md_path.relative_to(ROOT)).replace("\\", "/"),
        "created_at": now(),
        "real_action_executed": False
    }

    _append_jsonl(EVENTS_PATH, event)
    return event

def create_command_drafts_from_work_orders(limit: int = 10) -> dict:
    work_orders = load_work_orders(limit=100)
    existing = load_existing_command_drafts(limit=500)
    existing_sources = {item.get("source_work_order_id") for item in existing}

    pending = [item for item in work_orders if item.get("work_order_id") not in existing_sources]
    created = []

    for work_order in pending[:limit]:
        draft = build_command_draft_from_work_order(work_order)
        saved = save_command_draft(draft)
        created.append({
            "draft_id": draft.get("draft_id"),
            "source_work_order_id": draft.get("source_work_order_id"),
            "title": draft.get("title"),
            "risk": draft.get("risk"),
            "saved": saved
        })

    status = {
        "status": "KOS_LOCAL_COMMAND_COMPOSER_TICK_COMPLETED",
        "work_orders_seen": len(work_orders),
        "pending_work_orders_before_tick": len(pending),
        "created_command_drafts_count": len(created),
        "created_command_drafts": created,
        "gates": {
            "execute_allowed_now": False,
            "repo_write_allowed_now": False,
            "patch_apply_allowed_now": False,
            "arbitrary_shell_allowed": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_STATUS, status)
    _append_jsonl(EVENTS_PATH, status)
    return status

def get_latest_command_composer_status() -> dict:
    if LATEST_STATUS.exists():
        return _read_json(LATEST_STATUS)
    return create_command_drafts_from_work_orders(limit=1)

if __name__ == "__main__":
    print(json.dumps(create_command_drafts_from_work_orders(), ensure_ascii=False, indent=2))