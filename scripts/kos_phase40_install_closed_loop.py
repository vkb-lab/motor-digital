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
    "phase": "40",
    "module": "K-OS Closed Loop Autonomy",
    "mode": "SANDBOX_CLOSED_LOOP_ONLY",
    "goal": "executar o ciclo Missao -> Plano -> Aprovacao -> Executor Sandbox -> Relatorio sem acao externa real",
    "allowed_actions": {
        "create_mission": True,
        "plan_mission": True,
        "create_approval_request": True,
        "approve_dry_run": True,
        "run_safe_executor_bundle": True,
        "write_audit_report": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_access": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "external_side_effects": True
    },
    "safe_executor_actions": [
        "git_branch",
        "git_status"
    ],
    "required_confirmation": "YES_APPROVE_SAFE_DRY_RUN",
    "hard_rules": {
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "approval_required_before_safe_bundle": True,
        "safe_executor_allowlist_only": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

closed_loop_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

from k_atlas.kaizen.mission_queue import create_mission, plan_mission
from k_atlas.kaizen.human_approval import (
    create_approval_request,
    approve_dry_run,
    DRY_RUN_CONFIRMATION,
)
from k_atlas.kaizen.safe_executor import run_safe_bundle

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "closed_loop"
POLICY_PATH = ROOT / "config" / "kos_closed_loop_policy.json"

DEFAULT_SAFE_ACTIONS = ["git_branch", "git_status"]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _event(event: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event["created_at"] = now()
    with (LOG_DIR / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def run_closed_loop(
    title: str,
    description: str,
    priority: str = "high",
    typed_confirmation: str = "",
    safe_actions: list[str] | None = None,
) -> dict:
    loop_id = "KOS-LOOP-" + uuid.uuid4().hex[:10].upper()
    safe_actions = safe_actions or DEFAULT_SAFE_ACTIONS

    _event({
        "event": "closed_loop_started",
        "loop_id": loop_id,
        "title": title,
        "safe_actions": safe_actions,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    })

    mission = create_mission(
        title=title,
        description=description,
        priority=priority,
    )

    plan = plan_mission(mission["id"])

    approval = create_approval_request(
        title=f"Aprovar dry-run do loop {loop_id}",
        description="Aprovar somente execucao sandbox allowlist. Nenhuma acao externa real.",
        action_type="closed_loop_safe_bundle",
        risk_level="low",
        payload={
            "loop_id": loop_id,
            "mission_id": mission["id"],
            "safe_actions": safe_actions,
        },
    )

    approval_result = None
    executor_result = None

    if typed_confirmation.strip().upper() == DRY_RUN_CONFIRMATION:
        approval_result = approve_dry_run(approval["id"], typed_confirmation)

        if approval_result.get("ok") is True:
            executor_result = run_safe_bundle(
                bundle_id=loop_id,
                actions=safe_actions,
                dry_run=False,
            )
    else:
        approval_result = {
            "ok": False,
            "status": "WAITING_FOR_HUMAN_APPROVAL",
            "required_confirmation": DRY_RUN_CONFIRMATION,
            "execution_allowed": False,
        }

    status = "CLOSED_LOOP_SANDBOX_COMPLETED" if executor_result else "CLOSED_LOOP_WAITING_APPROVAL"

    report = {
        "status": status,
        "loop_id": loop_id,
        "mission": mission,
        "plan": plan,
        "approval_request": approval,
        "approval_result": approval_result,
        "executor_result": executor_result,
        "safe_actions": safe_actions,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    report_path = LOG_DIR / f"{loop_id}.json"
    _save_json(report_path, report)

    _event({
        "event": "closed_loop_finished",
        "loop_id": loop_id,
        "status": status,
        "executor_ran": executor_result is not None,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    })

    return report

def summarize_last_reports(limit: int = 10) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    reports = sorted(LOG_DIR.glob("KOS-LOOP-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    items = []
    for path in reports[:limit]:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            items.append({
                "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "loop_id": data.get("loop_id"),
                "status": data.get("status"),
                "mission_id": data.get("mission", {}).get("id"),
                "executor_ran": data.get("executor_result") is not None,
                "real_action_executed": data.get("real_action_executed"),
                "paid_ai_call_executed": data.get("paid_ai_call_executed"),
                "instagram_publish_executed": data.get("instagram_publish_executed"),
                "created_at": data.get("created_at"),
            })
        except Exception:
            pass

    return {
        "status": "CLOSED_LOOP_REPORTS_SUMMARY",
        "count": len(items),
        "reports": items,
    }

if __name__ == "__main__":
    result = run_closed_loop(
        title="Demo Fase 40",
        description="Rodar ciclo fechado seguro do K-OS sem publicacao, sem IA paga e sem acao externa.",
        priority="high",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=DEFAULT_SAFE_ACTIONS,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
'''

runner_code = r'''
from k_atlas.kaizen.closed_loop import run_closed_loop, summarize_last_reports
from k_atlas.kaizen.human_approval import DRY_RUN_CONFIRMATION
import json

if __name__ == "__main__":
    result = run_closed_loop(
        title="Fase 40 Closed Loop Demo",
        description="Executar ciclo Missao -> Plano -> Aprovacao -> Executor Sandbox -> Relatorio.",
        priority="high",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=["git_branch", "git_status"],
    )

    print(json.dumps({
        "status": "PHASE40_CLOSED_LOOP_DEMO_COMPLETED",
        "loop_status": result.get("status"),
        "loop_id": result.get("loop_id"),
        "executor_ran": result.get("executor_result") is not None,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "summary": summarize_last_reports(),
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.closed_loop import run_closed_loop, summarize_last_reports
from k_atlas.kaizen.human_approval import DRY_RUN_CONFIRMATION

st.set_page_config(page_title="KOS Closed Loop", layout="wide")

st.title("KOS Closed Loop Autonomy")
st.caption("Missao -> Plano -> Aprovacao -> Executor Sandbox -> Relatorio. Sem acao externa real.")

st.subheader("Novo ciclo fechado seguro")

title = st.text_input("Titulo", value="Nova missao closed loop")
description = st.text_area(
    "Descricao",
    value="Executar ciclo seguro em sandbox sem publicacao, sem IA paga e sem segredos."
)
priority = st.selectbox("Prioridade", ["high", "medium", "low"], index=0)

actions = st.multiselect(
    "Acoes seguras",
    ["git_branch", "git_status", "pytest_phase37"],
    default=["git_branch", "git_status"]
)

typed = st.text_input("Confirmacao", value="")

if st.button("Rodar ciclo fechado seguro", use_container_width=True):
    result = run_closed_loop(
        title=title,
        description=description,
        priority=priority,
        typed_confirmation=typed,
        safe_actions=actions,
    )
    st.json(result)

st.info(f"Confirmacao exigida para dry-run sandbox: {DRY_RUN_CONFIRMATION}")
st.warning("Nao publica, nao usa IA paga, nao executa Codex automaticamente e nao acessa segredos.")

st.subheader("Ultimos ciclos")
st.json(summarize_last_reports())
'''

test_code = r'''
from k_atlas.kaizen.closed_loop import run_closed_loop
from k_atlas.kaizen.human_approval import DRY_RUN_CONFIRMATION

def test_closed_loop_without_confirmation_waits():
    result = run_closed_loop(
        title="Teste sem aprovacao",
        description="Deve aguardar aprovacao humana.",
        priority="high",
        typed_confirmation="",
        safe_actions=["git_branch"],
    )

    assert result["status"] == "CLOSED_LOOP_WAITING_APPROVAL"
    assert result["executor_result"] is None
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False

def test_closed_loop_with_confirmation_runs_only_safe_executor():
    result = run_closed_loop(
        title="Teste com aprovacao dry-run",
        description="Deve rodar apenas safe executor allowlist.",
        priority="high",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=["git_branch"],
    )

    assert result["status"] == "CLOSED_LOOP_SANDBOX_COMPLETED"
    assert result["executor_result"] is not None
    assert result["executor_result"]["real_action_executed"] is False
    assert result["executor_result"]["paid_ai_call_executed"] is False
    assert result["executor_result"]["instagram_publish_executed"] is False

def test_closed_loop_blocks_unknown_action_via_safe_executor():
    result = run_closed_loop(
        title="Teste acao bloqueada",
        description="Safe executor deve bloquear acao fora da allowlist.",
        priority="medium",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=["instagram_publish"],
    )

    assert result["executor_result"] is not None
    assert result["executor_result"]["ok"] is False
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_closed_loop_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "closed_loop.py", closed_loop_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase40_closed_loop_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Closed_Loop.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase40_closed_loop.py", test_code.strip() + "\n")

report = {
    "status": "PHASE40_CLOSED_LOOP_BOOTSTRAPPED",
    "phase": "40",
    "created_files": [
        "config/kos_closed_loop_policy.json",
        "k_atlas/kaizen/closed_loop.py",
        "scripts/run_phase40_closed_loop_demo.py",
        "pages/KOS_Closed_Loop.py",
        "tests/test_phase40_closed_loop.py"
    ],
    "runtime_files": [
        "logs/kaizen/closed_loop/events.jsonl",
        "logs/kaizen/closed_loop/KOS-LOOP-*.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE40_CLOSED_LOOP_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))