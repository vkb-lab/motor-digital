
from pathlib import Path
from datetime import datetime
import argparse
import json
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
RUNTIME = ROOT / "local_runtime" / "kos_capability_executor"
EVENTS = RUNTIME / "events"

REPORTS.mkdir(exist_ok=True)
EVENTS.mkdir(parents=True, exist_ok=True)

BLOCKED_TERMS = [
    "publicar", "postar", "publish", "deploy", "enviar dm", "mandar dm",
    "comentar", "delete", "deletar", "apagar", "ia paga", "openai pago",
    "browser logado", "navegador logado", "scraping", "raspar", "senha", "token"
]

EXECUTORS = {
    "operational_master_audit": {
        "name": "Operational Master Audit",
        "script": "scripts/run_kos_operational_master_audit.py",
        "report": "reports/KOS_OPERATIONAL_MASTER_AUDIT_V1.json",
        "autonomy_level": 1,
        "permission": "local_readonly_report",
        "human_gate_required": False,
        "external_write": False
    },
    "hupmix_instagram_audit": {
        "name": "Hupmix Instagram Continuity Audit",
        "script": "scripts/run_kos_hupmix_instagram_continuity_audit.py",
        "report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
        "autonomy_level": 3,
        "permission": "meta_graph_readonly",
        "human_gate_required": False,
        "external_write": False
    },
    "gp_video_02_real_asset_audit": {
        "name": "GP_VIDEO_02 Real Asset Audit",
        "script": "scripts/run_kos_hupmix_gp_video_02_real_asset_audit.py",
        "report": "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json",
        "autonomy_level": 2,
        "permission": "local_asset_render",
        "human_gate_required": True,
        "external_write": False
    }
}

POLICY = {
    "max_autonomy_level": 3,
    "external_publish_enabled": False,
    "external_send_enabled": False,
    "paid_ai_enabled": False,
    "scraping_enabled": False,
    "logged_browser_automation_enabled": False,
    "safe_execution_modes": ["local_readonly_report", "local_asset_render", "meta_graph_readonly"]
}

def now():
    return datetime.now().isoformat()

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def normalize(text: str) -> str:
    value = str(text or "").lower().strip()
    table = str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc")
    return value.translate(table)

def has_blocked_intent(request: str):
    value = normalize(request)
    return [term for term in BLOCKED_TERMS if term in value]

def route_request(request: str):
    value = normalize(request)

    if any(term in value for term in ["hupmix", "garoto oxy", "oxy power", "gp_video_02", "gp video 02"]):
        return {
            "route": "hupmix_resolution_pipeline",
            "objective": "Auditar Hupmix e preparar continuidade GP_VIDEO_02 com assets reais.",
            "tasks": ["hupmix_instagram_audit", "gp_video_02_real_asset_audit"]
        }

    if any(term in value for term in ["auditar tudo", "autonomia", "capacidade", "capability", "agentes", "inteligencia conectada"]):
        return {
            "route": "operational_capability_audit",
            "objective": "Atualizar auditoria operacional e registry.",
            "tasks": ["operational_master_audit"]
        }

    return {
        "route": "status_only",
        "objective": "Motor pronto. Nenhuma tarefa operacional necessaria.",
        "tasks": []
    }

def can_execute(executor_id: str):
    spec = EXECUTORS.get(executor_id)
    if not spec:
        return False, "executor_not_found"

    if spec["autonomy_level"] > POLICY["max_autonomy_level"]:
        return False, "autonomy_level_above_policy"

    if spec["permission"] not in POLICY["safe_execution_modes"]:
        return False, "permission_not_allowed"

    if spec.get("external_write"):
        return False, "external_write_blocked"

    if not (ROOT / spec["script"]).exists():
        return False, "script_missing"

    return True, "allowed"

def run_executor(executor_id: str):
    spec = EXECUTORS[executor_id]
    allowed, reason = can_execute(executor_id)

    result = {
        "executor_id": executor_id,
        "name": spec.get("name"),
        "allowed": allowed,
        "reason": reason,
        "started_at": now(),
        "finished_at": None,
        "returncode": None,
        "report": spec.get("report"),
        "report_status": None,
        "stderr_tail": ""
    }

    if not allowed:
        result["finished_at"] = now()
        return result

    try:
        completed = subprocess.run(
            [sys.executable, spec["script"]],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=300
        )
        result["returncode"] = completed.returncode
        result["stderr_tail"] = (completed.stderr or "")[-2500:]

        report_data = load_json(ROOT / spec["report"])
        if isinstance(report_data, dict):
            result["report_status"] = report_data.get("status")
    except Exception as exc:
        result["returncode"] = -1
        result["stderr_tail"] = str(exc)

    result["finished_at"] = now()
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", default="status do motor")
    parser.add_argument("--no-execute", action="store_true")
    args = parser.parse_args()

    request = args.request
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    blocked_hits = has_blocked_intent(request)
    route = route_request(request)

    event = {
        "status": "KOS_CAPABILITY_EXECUTOR_RUN_READY",
        "run_id": run_id,
        "created_at": now(),
        "request": request,
        "blocked": bool(blocked_hits),
        "blocked_hits": blocked_hits,
        "route": route,
        "policy": POLICY,
        "executions": [],
        "next_step": None
    }

    if blocked_hits:
        event["status"] = "KOS_CAPABILITY_EXECUTOR_BLOCKED_BY_POLICY"
        event["next_step"] = "Acao externa bloqueada. Criar Human Gate separado se realmente necessario."
    elif not args.no_execute:
        for executor_id in route.get("tasks", []):
            event["executions"].append(run_executor(executor_id))

        gp_report = load_json(ROOT / "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json") or {}

        if route["route"] == "hupmix_resolution_pipeline":
            if gp_report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS":
                event["next_step"] = "Hupmix GP_VIDEO_02 aguardando assets reais em content_packs/hupmix_gp_video_02/assets_inbox."
            elif gp_report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_PREVIEW_READY":
                event["next_step"] = "Preview real pronto. Validar no Operator Chat e registrar OK humano."
            else:
                event["next_step"] = "Abrir estado Hupmix e revisar relatorio."
        else:
            event["next_step"] = "Execucao segura concluida."
    else:
        event["status"] = "KOS_CAPABILITY_EXECUTOR_PLAN_READY"
        event["next_step"] = "Plano criado sem execucao."

    event_path = EVENTS / f"{run_id}.json"
    last_path = RUNTIME / "last_run.json"

    event_path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    last_path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")

    status_report = {
        "status": "KOS_CAPABILITY_EXECUTOR_V1_READY",
        "runtime_last_run": rel(last_path),
        "runtime_events_dir": rel(EVENTS),
        "executors": EXECUTORS,
        "policy": POLICY,
        "note": "Runtime runs ficam em local_runtime para nao sujar Git."
    }

    status_path = REPORTS / "KOS_CAPABILITY_EXECUTOR_V1.json"
    old = load_json(status_path)
    if old != status_report:
        status_path.write_text(json.dumps(status_report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": event["status"],
        "run_id": run_id,
        "route": route["route"],
        "tasks": route["tasks"],
        "blocked": event["blocked"],
        "executions": [
            {
                "executor_id": item.get("executor_id"),
                "allowed": item.get("allowed"),
                "returncode": item.get("returncode"),
                "report_status": item.get("report_status")
            }
            for item in event["executions"]
        ],
        "next_step": event["next_step"],
        "event": rel(event_path),
        "last_run": rel(last_path)
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
