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
    "phase": "37",
    "module": "K-OS Mission Queue",
    "mode": "HUMAN_APPROVAL_REQUIRED",
    "goal": "registrar, planejar e preparar missoes para execucao segura sem executar automaticamente",
    "allowed_actions": {
        "create_mission": True,
        "plan_mission": True,
        "create_codex_draft": True,
        "approve_mission": True,
        "execute_mission": False,
        "publish_instagram": False,
        "call_paid_ai": False,
        "commit_without_firewall": False
    },
    "hard_rules": {
        "human_approval_required": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True,
        "codex_execution_manual_only": True
    },
    "created_at": now()
}

example_queue = {
    "status": "READY",
    "description": "Template versionavel. A fila real fica em local_runtime/kaizen/mission_queue.json",
    "missions": [
        {
            "id": "KOS-MISSION-EXAMPLE",
            "title": "Exemplo de missao segura",
            "description": "Planejar melhoria sem executar automaticamente.",
            "priority": "medium",
            "status": "draft",
            "approval_status": "not_requested",
            "execution_allowed": False
        }
    ],
    "created_at": now()
}

mission_queue_code = r'''
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "local_runtime" / "kaizen" / "mission_queue.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "missions"
POLICY_PATH = ROOT / "config" / "kos_mission_queue_policy.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Mission:
    id: str
    title: str
    description: str
    priority: str = "medium"
    status: str = "draft"
    approval_status: str = "not_requested"
    execution_allowed: bool = False
    created_at: str = ""
    updated_at: str = ""

def _load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _event(event: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event["created_at"] = now()
    path = LOG_DIR / "events.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def load_queue() -> dict:
    return _load_json(QUEUE_PATH, {
        "status": "READY",
        "missions": [],
        "created_at": now(),
        "updated_at": now()
    })

def save_queue(queue: dict) -> dict:
    queue["updated_at"] = now()
    _save_json(QUEUE_PATH, queue)
    return queue

def create_mission(title: str, description: str, priority: str = "medium") -> dict:
    queue = load_queue()

    mission = Mission(
        id="KOS-MISSION-" + uuid.uuid4().hex[:10].upper(),
        title=title.strip(),
        description=description.strip(),
        priority=priority.strip() or "medium",
        status="draft",
        approval_status="not_requested",
        execution_allowed=False,
        created_at=now(),
        updated_at=now()
    )

    queue.setdefault("missions", []).append(asdict(mission))
    save_queue(queue)

    _event({
        "event": "mission_created",
        "mission_id": mission.id,
        "title": mission.title,
        "execution_allowed": False
    })

    return asdict(mission)

def plan_mission(mission_id: str) -> dict:
    queue = load_queue()
    mission = None

    for item in queue.get("missions", []):
        if item.get("id") == mission_id:
            mission = item
            break

    if not mission:
        return {
            "ok": False,
            "status": "MISSION_NOT_FOUND",
            "mission_id": mission_id
        }

    try:
        from k_atlas.kaizen.planner_bridge import run_planner_bridge
        plan = run_planner_bridge(
            mission=mission.get("description", ""),
            mission_id=mission_id
        )
    except Exception as exc:
        plan = {
            "status": "PLANNER_BRIDGE_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }

    mission["status"] = "planned"
    mission["approval_status"] = "pending_human_review"
    mission["execution_allowed"] = False
    mission["updated_at"] = now()
    mission["last_plan"] = plan

    save_queue(queue)

    _event({
        "event": "mission_planned",
        "mission_id": mission_id,
        "execution_allowed": False,
        "planner_status": plan.get("status")
    })

    return {
        "ok": True,
        "status": "MISSION_PLANNED",
        "mission": mission,
        "plan": plan,
        "execution_allowed": False
    }

def approve_mission(mission_id: str, typed_confirmation: str) -> dict:
    queue = load_queue()
    required = "YES_APPROVE_DRY_RUN_ONLY"

    mission = None
    for item in queue.get("missions", []):
        if item.get("id") == mission_id:
            mission = item
            break

    if not mission:
        return {
            "ok": False,
            "status": "MISSION_NOT_FOUND",
            "mission_id": mission_id
        }

    if typed_confirmation.strip().upper() != required:
        return {
            "ok": False,
            "status": "APPROVAL_REJECTED",
            "reason": "confirmacao incorreta",
            "required": required,
            "execution_allowed": False
        }

    mission["approval_status"] = "approved_for_dry_run_only"
    mission["execution_allowed"] = False
    mission["status"] = "approved_dry_run"
    mission["updated_at"] = now()

    save_queue(queue)

    _event({
        "event": "mission_approved_dry_run_only",
        "mission_id": mission_id,
        "execution_allowed": False
    })

    return {
        "ok": True,
        "status": "MISSION_APPROVED_DRY_RUN_ONLY",
        "mission": mission,
        "execution_allowed": False
    }

def summarize_queue() -> dict:
    queue = load_queue()
    missions = queue.get("missions", [])
    return {
        "status": queue.get("status", "READY"),
        "total": len(missions),
        "draft": len([m for m in missions if m.get("status") == "draft"]),
        "planned": len([m for m in missions if m.get("status") == "planned"]),
        "approved_dry_run": len([m for m in missions if m.get("status") == "approved_dry_run"]),
        "execution_allowed_count": len([m for m in missions if m.get("execution_allowed") is True]),
        "queue_path": str(QUEUE_PATH),
        "missions": missions
    }

if __name__ == "__main__":
    mission = create_mission(
        title="Demo Fase 37",
        description="Planejar proximo incremento seguro do K-OS sem executar alteracoes.",
        priority="high"
    )
    planned = plan_mission(mission["id"])
    print(json.dumps({
        "created": mission,
        "planned": planned,
        "summary": summarize_queue(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

runner_code = r'''
from k_atlas.kaizen.mission_queue import create_mission, plan_mission, summarize_queue
import json

if __name__ == "__main__":
    mission = create_mission(
        title="Fase 37 Demo Mission",
        description="Gerar plano seguro para evoluir autonomia do K-OS usando Codex/Ollama em dry-run.",
        priority="high"
    )
    planned = plan_mission(mission["id"])

    print(json.dumps({
        "status": "PHASE37_DEMO_COMPLETED",
        "mission_id": mission["id"],
        "planned_status": planned.get("status"),
        "execution_allowed": False,
        "summary": summarize_queue(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import json
from pathlib import Path
import streamlit as st

from k_atlas.kaizen.mission_queue import create_mission, plan_mission, approve_mission, summarize_queue

st.set_page_config(page_title="KOS Mission Queue", layout="wide")

st.title("KOS Mission Queue")
st.caption("Fila de missoes com aprovacao humana. Nao executa acoes reais nesta fase.")

summary = summarize_queue()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", summary["total"])
col2.metric("Draft", summary["draft"])
col3.metric("Planned", summary["planned"])
col4.metric("Execution allowed", summary["execution_allowed_count"])

st.subheader("Criar missao")
title = st.text_input("Titulo", value="Nova missao K-OS")
description = st.text_area("Descricao", value="Planejar uma melhoria segura sem executar automaticamente.")
priority = st.selectbox("Prioridade", ["high", "medium", "low"], index=1)

if st.button("Criar missao", use_container_width=True):
    mission = create_mission(title, description, priority)
    st.success(f"Missao criada: {mission['id']}")
    st.rerun()

st.subheader("Missoes")
summary = summarize_queue()
missions = summary.get("missions", [])

if not missions:
    st.info("Nenhuma missao criada ainda.")
else:
    for mission in missions:
        with st.expander(f"{mission.get('id')} - {mission.get('title')}"):
            st.json(mission)

            if st.button(f"Planejar {mission.get('id')}", key="plan_" + mission.get("id")):
                result = plan_mission(mission.get("id"))
                st.json(result)
                st.rerun()

            typed = st.text_input(
                "Confirmacao dry-run",
                key="approve_input_" + mission.get("id"),
                value=""
            )

            if st.button(f"Aprovar dry-run {mission.get('id')}", key="approve_" + mission.get("id")):
                result = approve_mission(mission.get("id"), typed)
                st.json(result)
                st.rerun()

st.warning("Esta pagina nao publica, nao chama IA paga e nao executa Codex automaticamente.")
'''

test_code = r'''
from pathlib import Path
import json

from k_atlas.kaizen.mission_queue import create_mission, plan_mission, approve_mission, summarize_queue

def test_create_mission_safe():
    mission = create_mission(
        title="Teste seguro",
        description="Planejar sem executar.",
        priority="high"
    )
    assert mission["execution_allowed"] is False
    assert mission["approval_status"] == "not_requested"

def test_plan_mission_does_not_execute():
    mission = create_mission(
        title="Teste plano",
        description="Gerar plano dry-run.",
        priority="medium"
    )
    result = plan_mission(mission["id"])
    assert result["ok"] is True
    assert result["execution_allowed"] is False
    assert result["mission"]["status"] == "planned"

def test_approval_is_dry_run_only():
    mission = create_mission(
        title="Teste aprovacao",
        description="Aprovar apenas dry-run.",
        priority="medium"
    )
    result = approve_mission(mission["id"], "YES_APPROVE_DRY_RUN_ONLY")
    assert result["ok"] is True
    assert result["status"] == "MISSION_APPROVED_DRY_RUN_ONLY"
    assert result["execution_allowed"] is False
'''

save_json(ROOT / "config" / "kos_mission_queue_policy.json", policy)
save_json(ROOT / "memory" / "kaizen" / "mission_queue.example.json", example_queue)
write(ROOT / "k_atlas" / "kaizen" / "mission_queue.py", mission_queue_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase37_mission_queue_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Mission_Queue.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase37_mission_queue.py", test_code.strip() + "\n")

report = {
    "status": "PHASE37_MISSION_QUEUE_BOOTSTRAPPED",
    "phase": "37",
    "created_files": [
        "config/kos_mission_queue_policy.json",
        "memory/kaizen/mission_queue.example.json",
        "k_atlas/kaizen/mission_queue.py",
        "scripts/run_phase37_mission_queue_demo.py",
        "pages/KOS_Mission_Queue.py",
        "tests/test_phase37_mission_queue.py"
    ],
    "runtime_files": [
        "local_runtime/kaizen/mission_queue.json",
        "logs/kaizen/missions/events.jsonl"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE37_MISSION_QUEUE_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))