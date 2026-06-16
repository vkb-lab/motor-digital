from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]

COWORKER_TASKS_DIR = ROOT / "local_runtime" / "kos_local_coworker" / "tasks"
PATCH_DIR = ROOT / "local_runtime" / "kos_local_patch_workspace"
WORK_ORDERS_DIR = PATCH_DIR / "work_orders"
LOGS_DIR = PATCH_DIR / "logs"
LATEST_STATUS = PATCH_DIR / "latest_patch_workspace_status.json"
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

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_coworker_tasks(limit: int = 20) -> list[dict]:
    if not COWORKER_TASKS_DIR.exists():
        return []

    paths = sorted(COWORKER_TASKS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    tasks = []

    for path in paths:
        item = _read_json(path)
        if item:
            item["_source_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            tasks.append(item)

    return tasks

def proposed_files_for_task(task: dict) -> list[dict]:
    classification = task.get("classification", {}) or {}
    task_type = classification.get("task_type", "general_operation")
    body = str(task.get("body", "")).lower()
    title = str(task.get("title", "")).lower()
    scope_text = f"{title}\n{body}"

    # Ordem importa:
    # Fases mais especificas precisam vir antes de termos genericos como "runner gate".
    if (
        "fase 63" in scope_text
        or "phase 63" in scope_text
        or "product export packager" in scope_text
        or "export packager" in scope_text
        or task_type == "export_packager_operation"
    ):
        return [
            {"path": "config/kos_product_export_packager_policy.json", "purpose": "Policy do export packager local."},
            {"path": "k_atlas/product_factory/product_export_packager.py", "purpose": "Empacotador seguro read-only sem criar zip automaticamente."},
            {"path": "scripts/run_phase63_product_export_packager.py", "purpose": "Runner seguro da Fase 63."},
            {"path": "pages/KOS_Product_Export_Packager.py", "purpose": "Cockpit Streamlit da Fase 63."},
            {"path": "tests/test_phase63_product_export_packager.py", "purpose": "Testes de seguranca da Fase 63."},
            {"path": "reports/KOS_PHASE63_PRODUCT_EXPORT_PACKAGER_BOOTSTRAP.json", "purpose": "Relatorio auditavel da Fase 63."}
        ]

    if "fase 62" in scope_text or "phase 62" in scope_text or "runner gate" in scope_text:
        return [
            {"path": "config/kos_product_local_runner_gate_policy.json", "purpose": "Policy do runner gate local."},
            {"path": "k_atlas/product_factory/product_local_runner_gate.py", "purpose": "Gate read-only para preparar execucao local manual."},
            {"path": "scripts/run_phase62_product_local_runner_gate.py", "purpose": "Runner seguro da Fase 62."},
            {"path": "pages/KOS_Product_Local_Runner_Gate.py", "purpose": "Cockpit Streamlit da Fase 62."},
            {"path": "tests/test_phase62_product_local_runner_gate.py", "purpose": "Testes de seguranca da Fase 62."},
            {"path": "reports/KOS_PHASE62_PRODUCT_LOCAL_RUNNER_GATE_BOOTSTRAP.json", "purpose": "Relatorio da Fase 62."}
        ]

    if "fase 61" in scope_text or "phase 61" in scope_text or task_type == "local_autonomy_operation":
        return [
            {"path": "config/kos_local_patch_workspace_policy.json", "purpose": "Policy do workspace local de patches."},
            {"path": "k_atlas/kaizen/local_patch_workspace.py", "purpose": "Modulo de work orders locais."},
            {"path": "scripts/run_phase61b_local_patch_workspace.py", "purpose": "Runner seguro da fase."},
            {"path": "pages/KOS_Local_Patch_Workspace.py", "purpose": "Cockpit Streamlit da fase."},
            {"path": "tests/test_phase61b_local_patch_workspace.py", "purpose": "Testes de seguranca."},
            {"path": "reports/KOS_PHASE61B_LOCAL_PATCH_WORKSPACE_BOOTSTRAP.json", "purpose": "Relatorio da fase."}
        ]

    if task_type == "qa_operation":
        return [
            {"path": "k_atlas/product_factory/product_qa_gate.py", "purpose": "Ajuste futuro do QA gate se aprovado."},
            {"path": "tests/test_phase59_product_qa_gate.py", "purpose": "Testes relacionados ao QA gate."}
        ]

    return [
        {"path": "reports/KOS_LOCAL_WORK_ORDER_REVIEW_REQUIRED.json", "purpose": "Relatorio de revisao quando o escopo nao estiver claro."}
    ]

def build_operator_command_preview(work_order: dict) -> str:
    lines = [
        "$ErrorActionPreference=\"Stop\";",
        "Set-Location \"C:\\Users\\oi\\Desktop\\motor-digital\";",
        "",
        "Write-Host \"[KOS] Work order selecionada para revisao manual.\";",
        f"Write-Host \"[KOS] Work order: {work_order.get('work_order_id')}\";",
        "",
        "git --no-pager status --short;",
        "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status;",
        "",
        "Write-Host \"[KOS] Esta work order e somente um plano. Nenhuma alteracao aplicada automaticamente.\";"
    ]
    return "\n".join(lines)

def build_work_order_from_task(task: dict) -> dict:
    work_order_id = "KOS-WO-" + uuid.uuid4().hex[:12].upper()
    classification = task.get("classification", {}) or {}
    proposed_files = proposed_files_for_task(task)

    risk = classification.get("risk", "low")
    requires_engineer = risk in {"medium", "high"} or classification.get("ask_k_atlas_engineer") is True

    work_order = {
        "status": "KOS_LOCAL_PATCH_WORK_ORDER_READY",
        "work_order_id": work_order_id,
        "source_task_id": task.get("task_id"),
        "source_command_id": task.get("source_command_id"),
        "title": task.get("title"),
        "area": task.get("area"),
        "priority": task.get("priority"),
        "task_type": classification.get("task_type"),
        "risk": risk,
        "risk_reasons": classification.get("risk_reasons", []),
        "objective": task.get("body", ""),
        "proposed_repo_files": proposed_files,
        "test_plan": [
            "Rodar testes especificos da fase.",
            "Rodar testes regressivos relacionados.",
            "Rodar firewall staged antes de qualquer commit.",
            "Verificar git status final vazio."
        ],
        "operator_command_preview": "",
        "gates": {
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
            "ask_k_atlas_engineer": requires_engineer
        },
        "next_step": "Enviar esta work order para o K-Atlas Engineer revisar e converter em comando PowerShell completo.",
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    work_order["operator_command_preview"] = build_operator_command_preview(work_order)
    return work_order

def save_work_order(work_order: dict) -> dict:
    WORK_ORDERS_DIR.mkdir(parents=True, exist_ok=True)
    path = WORK_ORDERS_DIR / f"{work_order['work_order_id']}.json"
    _write_json(path, work_order)

    event = {
        "status": "KOS_LOCAL_PATCH_WORK_ORDER_SAVED",
        "work_order_id": work_order.get("work_order_id"),
        "source_task_id": work_order.get("source_task_id"),
        "title": work_order.get("title"),
        "risk": work_order.get("risk"),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "created_at": now(),
        "real_action_executed": False
    }

    _append_jsonl(EVENTS_PATH, event)
    return event

def load_existing_work_orders(limit: int = 20) -> list[dict]:
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

def create_work_orders_from_coworker_tasks(limit: int = 5) -> dict:
    tasks = load_coworker_tasks(limit=50)
    existing = load_existing_work_orders(limit=200)
    existing_sources = {item.get("source_task_id") for item in existing}

    pending = [task for task in tasks if task.get("task_id") not in existing_sources]
    created = []

    for task in pending[:limit]:
        work_order = build_work_order_from_task(task)
        saved = save_work_order(work_order)
        created.append({
            "work_order_id": work_order.get("work_order_id"),
            "source_task_id": work_order.get("source_task_id"),
            "title": work_order.get("title"),
            "risk": work_order.get("risk"),
            "task_type": work_order.get("task_type"),
            "saved": saved
        })

    status = {
        "status": "KOS_LOCAL_PATCH_WORKSPACE_TICK_COMPLETED",
        "tasks_seen": len(tasks),
        "pending_tasks_before_tick": len(pending),
        "created_work_orders_count": len(created),
        "created_work_orders": created,
        "gates": {
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

def get_latest_patch_workspace_status() -> dict:
    if LATEST_STATUS.exists():
        return _read_json(LATEST_STATUS)
    return create_work_orders_from_coworker_tasks(limit=1)

if __name__ == "__main__":
    print(json.dumps(create_work_orders_from_coworker_tasks(), ensure_ascii=False, indent=2))