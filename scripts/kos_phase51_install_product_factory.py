from pathlib import Path
from datetime import datetime, timezone
import json
import re

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
    "phase": "51",
    "module": "K-OS Product Factory Mission Layer",
    "mode": "MISSION_DESIGN_ONLY",
    "goal": "transformar ideias de produto em missoes estruturadas, auditaveis e seguras",
    "allowed_product_types": [
        "saas",
        "app",
        "landing_page",
        "campaign",
        "automation",
        "api",
        "agent",
        "dashboard",
        "integration"
    ],
    "allowed_actions": {
        "create_product_mission": True,
        "classify_product_type": True,
        "generate_safe_task_plan": True,
        "write_local_runtime_mission": True,
        "summarize_product_missions": True
    },
    "blocked_actions": {
        "build_product_automatically": True,
        "deploy_automatically": True,
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "auto_commit": True,
        "auto_push": True
    },
    "hard_rules": {
        "draft_only": True,
        "human_approval_required_before_execution": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

mission_layer_code = r'''
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
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import (
    create_product_mission,
    summarize_product_missions,
    export_to_kaizen_mission_dry_run,
)

if __name__ == "__main__":
    mission = create_product_mission(
        idea="Primeira missao Product Factory do K-OS",
        product_type="saas",
        target_user="pequenos negocios que precisam de automacao e marketing",
        market="SaaS operacional com IA modular",
        priority="medium",
        source="phase51_runner"
    )

    print(json.dumps({
        "status": "PHASE51_PRODUCT_FACTORY_MISSION_CREATED",
        "mission_id": mission.get("mission_id"),
        "title": mission.get("title"),
        "product_type": mission.get("product_type"),
        "tasks_count": len(mission.get("tasks", [])),
        "summary": summarize_product_missions(limit=10),
        "export_dry_run": export_to_kaizen_mission_dry_run(mission),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.product_factory.mission_layer import (
    build_product_mission,
    append_product_mission,
    summarize_product_missions,
    export_to_kaizen_mission_dry_run,
)

st.set_page_config(page_title="KOS Product Factory", layout="wide")

st.title("KOS Product Factory Mission Layer")
st.caption("Transforma ideias em missoes estruturadas. Nao executa build, deploy ou publicacao.")

idea = st.text_input("Ideia", "Criar um SaaS simples de automacao comercial com IA")
product_type = st.selectbox(
    "Tipo",
    ["saas", "app", "landing_page", "campaign", "automation", "api", "agent", "dashboard", "integration"]
)
target_user = st.text_input("Publico-alvo", "pequenos negocios")
market = st.text_input("Mercado", "automacao e marketing")
priority = st.selectbox("Prioridade", ["low", "medium", "high"], index=1)

draft = build_product_mission(
    idea=idea,
    product_type=product_type,
    target_user=target_user,
    market=market,
    priority=priority,
    source="streamlit_draft"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tipo", draft.get("product_type"))
col2.metric("Tasks", len(draft.get("tasks", [])))
col3.metric("Execution", "BLOQUEADA")
col4.metric("Risk", draft.get("risk_level"))

st.subheader("Missao draft")
st.json(draft)

st.subheader("Export dry-run")
st.json(export_to_kaizen_mission_dry_run(draft))

if st.button("Salvar missao local", use_container_width=True):
    saved = append_product_mission(draft)
    st.success("Missao salva no runtime local.")
    st.json(saved)

st.subheader("Resumo")
st.json(summarize_product_missions(limit=20))

st.warning("Design-only. Sem IA paga, sem Instagram, sem Codex automatico, sem deploy.")
'''

test_code = r'''
from k_atlas.product_factory.mission_layer import (
    build_product_mission,
    create_product_mission,
    summarize_product_missions,
    export_to_kaizen_mission_dry_run,
)

def test_build_product_mission_is_safe():
    mission = build_product_mission(
        idea="Criar SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste",
        priority="medium",
        source="test"
    )

    assert mission["status"] == "PRODUCT_FACTORY_MISSION_READY"
    assert mission["gates"]["execution_allowed"] is False
    assert mission["gates"]["paid_ai_allowed"] is False
    assert mission["gates"]["instagram_publish_allowed"] is False
    assert mission["real_action_executed"] is False
    assert mission["paid_ai_call_executed"] is False
    assert mission["instagram_publish_executed"] is False
    assert mission["external_side_effects_executed"] is False

def test_invalid_product_type_defaults_to_saas():
    mission = build_product_mission(
        idea="Produto invalido",
        product_type="unknown",
        target_user="teste",
        market="teste"
    )

    assert mission["product_type"] == "saas"

def test_create_and_summarize_product_mission():
    mission = create_product_mission(
        idea="Landing page de teste",
        product_type="landing_page",
        target_user="teste",
        market="teste",
        source="test_phase51"
    )

    summary = summarize_product_missions(limit=5)

    assert mission["mission_id"]
    assert summary["status"] == "PRODUCT_FACTORY_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False

def test_export_to_kaizen_is_dry_run():
    mission = build_product_mission(
        idea="Agente de teste",
        product_type="agent",
        target_user="operador",
        market="IA"
    )

    export = export_to_kaizen_mission_dry_run(mission)

    assert export["status"] == "PRODUCT_MISSION_EXPORT_DRY_RUN_READY"
    assert export["dry_run"] is True
    assert export["execution_allowed"] is False
    assert export["real_action_executed"] is False
'''

save_json(ROOT / "config" / "kos_product_factory_policy.json", policy)
write(ROOT / "k_atlas" / "product_factory" / "__init__.py", "from .mission_layer import build_product_mission, create_product_mission, summarize_product_missions\n")
write(ROOT / "k_atlas" / "product_factory" / "mission_layer.py", mission_layer_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase51_product_factory_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Product_Factory.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase51_product_factory.py", test_code.strip() + "\n")

report = {
    "status": "PHASE51_PRODUCT_FACTORY_MISSION_LAYER_BOOTSTRAPPED",
    "phase": "51",
    "created_files": [
        "config/kos_product_factory_policy.json",
        "k_atlas/product_factory/__init__.py",
        "k_atlas/product_factory/mission_layer.py",
        "scripts/run_phase51_product_factory_demo.py",
        "pages/KOS_Product_Factory.py",
        "tests/test_phase51_product_factory.py"
    ],
    "runtime_files": [
        "local_runtime/product_factory/product_missions.jsonl",
        "local_runtime/product_factory/latest_product_factory_summary.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE51_PRODUCT_FACTORY_MISSION_LAYER_BOOTSTRAP.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))