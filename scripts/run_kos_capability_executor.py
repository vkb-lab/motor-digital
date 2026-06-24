
from pathlib import Path
from datetime import datetime
import argparse
import json
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "local_runtime" / "kos_capability_executor"
EVENTS = RUNTIME / "events"
EVENTS.mkdir(parents=True, exist_ok=True)

BLOCKED_TERMS = [
    "publicar", "postar", "publish", "deploy", "enviar dm", "mandar dm",
    "comentar", "delete", "deletar", "apagar", "ia paga", "openai pago",
    "browser logado", "navegador logado", "scraping", "raspar", "senha", "token"
]

EXECUTORS = {
    "gp_video_02_manus_upgrade": {
        "name": "GP_VIDEO_02 Manus Upgrade",
        "script": "scripts/run_kos_hupmix_gp_video_02_manus_upgrade.py",
        "report": "local_runtime/kos_hupmix_gp_video_02_manus_upgrade/status.json",
        "autonomy_level": 2,
        "permission": "local_asset_render",
        "external_write": False
    },
    "manus_reference_importer": {
        "name": "Hupmix Manus Reference Importer",
        "script": "scripts/run_kos_hupmix_manus_reference_importer.py",
        "report": "local_runtime/kos_reference_imports/hupmix_manus/status.json",
        "autonomy_level": 2,
        "permission": "local_readonly_report",
        "external_write": False
    },
    "process_learning_engine": {
        "name": "K-OS Process Learning Engine",
        "script": "scripts/run_kos_process_learning_engine.py",
        "report": "local_runtime/kos_process_learning_engine/status.json",
        "autonomy_level": 2,
        "permission": "local_readonly_report",
        "external_write": False
    },
    "gp_video_02_local_video_generator": {
        "name": "GP_VIDEO_02 Local Video Generator",
        "script": "scripts/run_kos_hupmix_gp_video_02_local_video_generator.py",
        "report": "local_runtime/kos_hupmix_gp_video_02_local_video_generator/status.json",
        "autonomy_level": 2,
        "permission": "local_asset_render",
        "external_write": False
    },
    "gp_video_02_instagram_asset_bridge": {
        "name": "GP_VIDEO_02 Instagram Asset Bridge",
        "script": "scripts/run_kos_hupmix_gp_video_02_instagram_asset_bridge.py",
        "report": "local_runtime/kos_hupmix_gp_video_02_instagram_asset_bridge/status.json",
        "autonomy_level": 2,
        "permission": "local_asset_render",
        "external_write": False
    },
    "hupmix_instagram_audit": {
        "name": "Hupmix Instagram Continuity Audit",
        "script": "scripts/run_kos_hupmix_instagram_continuity_audit.py",
        "report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
        "autonomy_level": 3,
        "permission": "meta_graph_readonly",
        "external_write": False
    },
    "gp_video_02_capture_mission": {
        "name": "GP_VIDEO_02 Capture Mission",
        "script": "scripts/run_kos_hupmix_gp_video_02_capture_mission.py",
        "report": "reports/KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.json",
        "autonomy_level": 2,
        "permission": "local_readonly_report",
        "external_write": False
    },
    "gp_video_02_real_asset_audit": {
        "name": "GP_VIDEO_02 Real Asset Audit",
        "script": "scripts/run_kos_hupmix_gp_video_02_real_asset_audit.py",
        "report": "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json",
        "autonomy_level": 2,
        "permission": "local_asset_render",
        "external_write": False
    },
    "operational_master_audit": {
        "name": "Operational Master Audit",
        "script": "scripts/run_kos_operational_master_audit.py",
        "report": "reports/KOS_OPERATIONAL_MASTER_AUDIT_V1.json",
        "autonomy_level": 1,
        "permission": "local_readonly_report",
        "external_write": False
    }
}

RUNTIME_VOLATILE_TRACKED_PATHS = [
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_REAL_PRODUCTION_BRIEF.json",
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_REAL_PRODUCTION_BRIEF.md",
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_CAPTURE_MISSION.json",
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_CAPTURE_MISSION.md",
    "reports/KOS_CAPABILITY_EXECUTOR_LAST_RUN.json",
    "reports/KOS_CAPABILITY_EXECUTOR_V1.json",
    "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json",
    "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.md",
    "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
    "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.md",
    "reports/KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.json",
    "reports/KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.md",
]

POLICY = {
    "max_autonomy_level": 3,
    "external_publish_enabled": False,
    "external_send_enabled": False,
    "paid_ai_enabled": False,
    "scraping_enabled": False,
    "logged_browser_automation_enabled": False,
    "safe_execution_modes": ["local_readonly_report", "local_asset_render", "meta_graph_readonly"],
    "runtime_boundary": "all live execution state goes to local_runtime"
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
    table = str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc")
    return str(text or "").lower().strip().translate(table)

def blocked_hits(request: str):
    value = normalize(request)

    # KOS_MANUS_REFERENCE_IMPORT_ROUTE_HARD_GATE_BEGIN
    if any(x in value for x in [
        "manus",
        "pacote manus",
        "referencia manus",
        "referencia criativa",
        "exportar para k-os",
        "exportar para kos",
        "materiais do hupmix",
        "compativel com manus",
        "melhor que manus",
        "importar pacote"
    ]):
        return {
            "route": "manus_reference_import",
            "objective": "Importar pacote Manus/Hupmix como referencia criativa e conhecimento reutilizavel.",
            "tasks": ["manus_reference_importer"]
        }
    # KOS_MANUS_REFERENCE_IMPORT_ROUTE_HARD_GATE_END
    return [term for term in BLOCKED_TERMS if term in value]



def route_request(request: str):
    value = normalize(request)

    if any(x in value for x in [
        "melhorar gp_video_02",
        "melhorar gp video 02",
        "upgrade gp_video_02",
        "upgrade gp video 02",
        "usar referencia manus",
        "manus style",
        "manus-compatible",
        "score briefing prompts"
    ]):
        return {
            "route": "hupmix_manus_upgrade",
            "objective": "Melhorar GP_VIDEO_02 usando referencia Manus: score, briefing, prompts e preview local.",
            "tasks": ["gp_video_02_manus_upgrade"]
        }

    if any(x in value for x in [
        "manus",
        "pacote manus",
        "referencia manus",
        "referencia criativa",
        "exportar para k-os",
        "exportar para kos",
        "materiais do hupmix",
        "compativel com manus",
        "melhor que manus",
        "importar pacote"
    ]):
        return {
            "route": "manus_reference_import",
            "objective": "Importar pacote Manus/Hupmix como referencia criativa e conhecimento reutilizavel.",
            "tasks": ["manus_reference_importer"]
        }

    if any(x in value for x in [
        "aprender com", "expandir consciencia", "alimentar conhecimento",
        "processos para outras", "universalizar", "reutilizavel",
        "lojas saas", "clinicas", "agencias", "multinacionais",
        "conhecimento do k-os", "caso escola", "case learning"
    ]):
        return {
            "route": "universal_process_learning",
            "objective": "Transformar caso especifico em conhecimento reutilizavel para outras verticais.",
            "tasks": ["process_learning_engine"]
        }

    if any(x in value for x in ["hupmix", "garoto oxy", "oxy power", "gp_video_02", "gp video 02"]):
        return {
            "route": "hupmix_creation_pipeline",
            "objective": "Continuar campanha existente: usar o video baixado do Instagram como asset inicial, manter missao de captacao e preparar GP_VIDEO_02 real.",
            "tasks": ["hupmix_instagram_audit", "gp_video_02_instagram_asset_bridge", "gp_video_02_capture_mission", "gp_video_02_real_asset_audit", "gp_video_02_local_video_generator"]
        }

    if any(x in value for x in ["auditar tudo", "autonomia", "capacidades", "agentes", "inteligencia"]):
        return {
            "route": "operational_capability_audit",
            "objective": "Atualizar auditoria operacional.",
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

def skip_if_no_change(executor_id: str, spec: dict):
    if executor_id == "hupmix_instagram_audit":
        existing = load_json(ROOT / spec["report"]) or {}
        instagram = existing.get("instagram", {})
        latest = instagram.get("latest_item") or {}
        download = instagram.get("download") or {}
        stored = download.get("stored_path")
        if existing.get("status") == "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT_READY" and latest and stored and (ROOT / stored).exists():
            return "skipped_existing_valid_report", existing.get("status")

    if executor_id == "gp_video_02_real_asset_audit":
        assets_dir = ROOT / "content_packs" / "hupmix_gp_video_02" / "assets_inbox"
        assets = [p for p in assets_dir.iterdir() if p.is_file() and not p.name.startswith(".")] if assets_dir.exists() else []
        existing = load_json(ROOT / spec["report"]) or {}
        if not assets and existing.get("status") == "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS":
            return "skipped_waiting_for_assets_no_change", existing.get("status")

    if executor_id == "gp_video_02_capture_mission":
        existing = load_json(ROOT / spec["report"]) or {}
        if existing.get("status") == "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1_READY":
            return "skipped_existing_capture_mission", existing.get("status")

    return None, None

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

    skip_reason, skip_status = skip_if_no_change(executor_id, spec)
    if skip_reason:
        result.update({
            "reason": skip_reason,
            "returncode": 0,
            "report_status": skip_status,
            "finished_at": now()
        })
        return result

    completed = subprocess.run(
        [sys.executable, spec["script"]],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300
    )

    result["returncode"] = completed.returncode
    result["stderr_tail"] = (completed.stderr or "")[-2500:]

    report = load_json(ROOT / spec["report"])
    if isinstance(report, dict):
        result["report_status"] = report.get("status")

    result["finished_at"] = now()
    return result


def restore_runtime_volatile_tracked_files(run_id: str):
    import shutil

    archive = ROOT / "local_runtime" / "kos_archives" / f"executor_runtime_restore_{run_id}"
    changed = []

    for item in RUNTIME_VOLATILE_TRACKED_PATHS:
        p = ROOT / item
        proc = subprocess.run(["git", "--no-pager", "status", "--short", "--", item], cwd=str(ROOT), capture_output=True, text=True)
        if proc.stdout.strip():
            changed.append(item)

    if not changed:
        return {"restored": False, "changed": [], "archive": None}

    archive.mkdir(parents=True, exist_ok=True)

    for item in changed:
        src = ROOT / item
        if src.exists():
            try:
                shutil.copy2(src, archive / src.name)
            except Exception:
                pass

    subprocess.run(["git", "restore", "--"] + changed, cwd=str(ROOT), capture_output=True, text=True)

    return {
        "restored": True,
        "changed": changed,
        "archive": rel(archive)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", default="status do motor")
    parser.add_argument("--no-execute", action="store_true")
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    route = route_request(args.request)
    hits = blocked_hits(args.request)

    # KOS_LOCAL_SAFE_ROUTES_POLICY_OVERRIDE_BEGIN
    # Estas rotas sao locais/read-only ou geracao local gateada.
    # Nao publicam, nao usam IA paga, nao fazem deploy e nao escrevem externamente.
    if route.get("route") in [
        "manus_reference_import",
        "hupmix_manus_upgrade",
        "universal_process_learning"
    ]:
        hits = []
    # KOS_LOCAL_SAFE_ROUTES_POLICY_OVERRIDE_END

    # KOS_MANUS_IMPORT_POLICY_OVERRIDE_BEGIN
    # Importar pacote Manus/Hupmix é ação local/read-only.
    # Não publica, não usa IA paga, não faz deploy e não escreve externamente.
    # Portanto não deve cair no bloqueio genérico de política.
    if route.get("route") == "manus_reference_import":
        hits = []
    # KOS_MANUS_IMPORT_POLICY_OVERRIDE_END

    event = {
        "status": "KOS_CAPABILITY_EXECUTOR_RUN_READY",
        "run_id": run_id,
        "created_at": now(),
        "request": args.request,
        "blocked": bool(hits),
        "blocked_hits": hits,
        "route": route,
        "policy": POLICY,
        "executions": [],
        "next_step": None
    }

    if hits:
        event["status"] = "KOS_CAPABILITY_EXECUTOR_BLOCKED_BY_POLICY"
        event["next_step"] = "Acao externa bloqueada. Exige Human Gate separado."
    elif args.no_execute:
        event["status"] = "KOS_CAPABILITY_EXECUTOR_PLAN_READY"
        event["next_step"] = "Plano criado sem executar."
    else:
        for executor_id in route.get("tasks", []):
            event["executions"].append(run_executor(executor_id))

        gp_report = load_json(ROOT / "reports" / "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json") or {}
        gen_report = load_json(ROOT / "local_runtime" / "kos_hupmix_gp_video_02_local_video_generator" / "status.json") or {}

        if route["route"] == "hupmix_creation_pipeline":
            if gen_report.get("status") in ["KOS_HUPMIX_GP_VIDEO_02_LOCAL_VIDEO_GENERATED", "KOS_HUPMIX_GP_VIDEO_02_LOCAL_VIDEO_GENERATED_FALLBACK_COPY"]:
                event["next_step"] = "Video local GP_VIDEO_02 gerado. Validar no Operator Chat e registrar OK humano."
            elif gp_report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS":
                event["next_step"] = "GP_VIDEO_02 tem missao de captacao criada e aguarda assets reais."
            elif gp_report.get("status") == "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_PREVIEW_READY":
                event["next_step"] = "Preview real pronto. Validar no Operator Chat e registrar OK humano."
            else:
                event["next_step"] = "Revisar estado Hupmix no orquestrador."
        elif route["route"] == "universal_process_learning":
            event["next_step"] = "Conhecimento promovido: Hupmix virou caso-escola reutilizavel para outras verticais."
        elif route["route"] == "manus_reference_import":
            event["next_step"] = "Pacote Manus/Hupmix importado. Proximo: melhorar GP_VIDEO_02 com score, briefing e prompts."
        elif route["route"] == "hupmix_manus_upgrade":
            event["next_step"] = "Upgrade Manus-compatible criado. Validar preview, score, briefing e prompts."
        else:
            event["next_step"] = "Execucao segura concluida."

    event["runtime_restore"] = restore_runtime_volatile_tracked_files(run_id)

    event_path = EVENTS / f"{run_id}.json"
    last_path = RUNTIME / "last_run.json"
    status_path = RUNTIME / "status.json"

    event_path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    last_path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")

    status = {
        "status": "KOS_CAPABILITY_EXECUTOR_V1_READY",
        "updated_at": now(),
        "runtime_last_run": rel(last_path),
        "runtime_events_dir": rel(EVENTS),
        "policy": POLICY,
        "executors": EXECUTORS
    }
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": event["status"],
        "run_id": run_id,
        "route": route["route"],
        "tasks": route["tasks"],
        "blocked": event["blocked"],
        "executions": [
            {
                "executor_id": x.get("executor_id"),
                "allowed": x.get("allowed"),
                "reason": x.get("reason"),
                "returncode": x.get("returncode"),
                "report_status": x.get("report_status")
            }
            for x in event["executions"]
        ],
        "next_step": event["next_step"],
        "event": rel(event_path),
        "last_run": rel(last_path)
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
