from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import uuid

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "local_runtime" / "product_factory"
MISSION_LOG = RUNTIME_DIR / "product_missions.jsonl"
SUMMARY_PATH = RUNTIME_DIR / "latest_product_factory_summary.json"

ALLOWED_PRODUCT_TYPES = {
    "saas",
    "app",
    "landing_page",
    "campaign",
    "automation",
    "api",
    "agent",
    "dashboard",
    "integration",
}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "product-mission"

def normalize_product_type(product_type: str) -> str:
    value = (product_type or "saas").strip().lower()
    if value not in ALLOWED_PRODUCT_TYPES:
        return "saas"
    return value

def default_tasks(product_type: str) -> list[dict]:
    base = [
        ("discovery", "Definir problema, publico, promessa e criterio de sucesso."),
        ("offer", "Organizar proposta de valor, nome, headline e oferta inicial."),
        ("scope", "Definir MVP minimo, limites e entregaveis da primeira versao."),
        ("architecture", "Propor arquitetura tecnica modular sem executar build."),
        ("assets", "Listar paginas, textos, criativos, dados e automacoes necessarias."),
        ("governance", "Definir travas, aprovacoes humanas, logs e rollback."),
        ("launch_plan", "Criar plano de lancamento seguro, ainda sem publicar.")
    ]

    if product_type == "campaign":
        base.insert(3, ("campaign_strategy", "Definir canais, calendario, narrativa e CTA."))
    elif product_type == "agent":
        base.insert(3, ("agent_role", "Definir papel, permissoes, memoria e limites do agente."))
    elif product_type == "automation":
        base.insert(3, ("automation_flow", "Mapear gatilhos, entradas, saidas e logs."))
    elif product_type == "api":
        base.insert(3, ("api_contract", "Rascunhar endpoints, payloads, erros e autenticacao futura."))
    elif product_type == "landing_page":
        base.insert(3, ("landing_sections", "Definir secoes, copy, prova, CTA e formulario."))
    elif product_type == "dashboard":
        base.insert(3, ("dashboard_metrics", "Definir metricas, fontes de dados e visualizacoes."))
    elif product_type == "integration":
        base.insert(3, ("integration_contract", "Definir sistemas, credenciais locais futuras e limites."))
    elif product_type == "app":
        base.insert(3, ("app_flow", "Definir telas, estados, fluxo principal e persistencia."))
    else:
        base.insert(3, ("saas_model", "Definir modulo SaaS, plano, usuarios e operacao."))

    return [
        {
            "task_id": f"TASK-{index:02d}",
            "key": key,
            "title": title,
            "status": "proposed",
            "execution_allowed": False,
            "requires_human_approval": True
        }
        for index, (key, title) in enumerate(base, start=1)
    ]

def build_product_mission(
    idea: str,
    product_type: str = "saas",
    target_user: str = "cliente ideal ainda nao definido",
    market: str = "mercado ainda nao definido",
    priority: str = "medium",
    source: str = "manual"
) -> dict:
    product_type = normalize_product_type(product_type)
    title = (idea or "Nova missao de produto").strip()
    slug = slugify(title)

    mission = {
        "status": "PRODUCT_FACTORY_MISSION_READY",
        "mission_id": "PFM-" + uuid.uuid4().hex[:12].upper(),
        "title": title,
        "slug": slug,
        "product_type": product_type,
        "target_user": target_user,
        "market": market,
        "priority": priority,
        "source": source,
        "stage": "draft",
        "execution_mode": "DESIGN_ONLY",
        "tasks": default_tasks(product_type),
        "gates": {
            "human_approval_required": True,
            "execution_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "codex_auto_execute_allowed": False,
            "external_publish_allowed": False
        },
        "outputs_expected": [
            "product_brief",
            "mvp_scope",
            "technical_plan",
            "asset_plan",
            "launch_plan",
            "risk_register"
        ],
        "risk_level": "low",
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    return mission

def append_product_mission(mission: dict) -> dict:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    with MISSION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(mission, ensure_ascii=False) + "\n")

    summary = summarize_product_missions(limit=20)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return mission

def create_product_mission(**kwargs) -> dict:
    mission = build_product_mission(**kwargs)
    return append_product_mission(mission)

def summarize_product_missions(limit: int = 20) -> dict:
    entries = []

    if MISSION_LOG.exists():
        lines = MISSION_LOG.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass

    latest = entries[-1] if entries else {}

    by_type = {}
    for item in entries:
        ptype = item.get("product_type", "unknown")
        by_type[ptype] = by_type.get(ptype, 0) + 1

    return {
        "status": "PRODUCT_FACTORY_SUMMARY_READY",
        "mission_log_exists": MISSION_LOG.exists(),
        "mission_log_path": str(MISSION_LOG.relative_to(ROOT)).replace("\\", "/"),
        "entries_returned": len(entries),
        "latest_mission_id": latest.get("mission_id"),
        "latest_title": latest.get("title"),
        "latest_product_type": latest.get("product_type"),
        "by_type": by_type,
        "last_entries": entries,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def export_to_kaizen_mission_dry_run(product_mission: dict) -> dict:
    return {
        "status": "PRODUCT_MISSION_EXPORT_DRY_RUN_READY",
        "source_mission_id": product_mission.get("mission_id"),
        "target_queue": "kaizen_mission_queue",
        "would_create": {
            "title": product_mission.get("title"),
            "mission_type": "product_factory",
            "priority": product_mission.get("priority", "medium"),
            "tasks_count": len(product_mission.get("tasks", []))
        },
        "dry_run": True,
        "execution_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

if __name__ == "__main__":
    mission = create_product_mission(
        idea="K-OS Product Factory demo mission",
        product_type="saas",
        target_user="operador K-OS",
        market="automacao inteligente",
        priority="medium",
        source="phase51_manual"
    )
    print(json.dumps({
        "mission": mission,
        "summary": summarize_product_missions(),
        "export_dry_run": export_to_kaizen_mission_dry_run(mission)
    }, ensure_ascii=False, indent=2))
