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
    "phase": "39",
    "module": "K-OS Human Approval Console",
    "mode": "APPROVAL_LEDGER_ONLY",
    "goal": "registrar aprovacoes humanas auditaveis sem liberar execucao real automatica",
    "allowed_actions": {
        "create_approval_request": True,
        "approve_dry_run": True,
        "reject_request": True,
        "list_requests": True
    },
    "blocked_actions": {
        "approve_real_publish": True,
        "approve_paid_ai": True,
        "approve_secret_access": True,
        "execute_codex_automatically": True,
        "publish_instagram": True
    },
    "required_confirmation": {
        "dry_run_only": "YES_APPROVE_SAFE_DRY_RUN"
    },
    "hard_rules": {
        "approval_does_not_execute": True,
        "execution_allowed_remains_false": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

human_approval_code = r'''
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "local_runtime" / "kaizen" / "human_approvals.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "approvals"
POLICY_PATH = ROOT / "config" / "kos_human_approval_policy.json"

DRY_RUN_CONFIRMATION = "YES_APPROVE_SAFE_DRY_RUN"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class ApprovalRequest:
    id: str
    title: str
    description: str
    action_type: str
    risk_level: str
    payload: dict
    status: str = "pending"
    approval_scope: str = "dry_run_only"
    execution_allowed: bool = False
    real_action_allowed: bool = False
    paid_ai_allowed: bool = False
    external_publish_allowed: bool = False
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
    with (LOG_DIR / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def load_ledger() -> dict:
    return _load_json(LEDGER_PATH, {
        "status": "READY",
        "requests": [],
        "created_at": now(),
        "updated_at": now()
    })

def save_ledger(ledger: dict) -> dict:
    ledger["updated_at"] = now()
    _save_json(LEDGER_PATH, ledger)
    return ledger

def create_approval_request(
    title: str,
    description: str,
    action_type: str = "safe_dry_run",
    risk_level: str = "low",
    payload: dict | None = None,
) -> dict:
    ledger = load_ledger()

    request = ApprovalRequest(
        id="KOS-APPROVAL-" + uuid.uuid4().hex[:10].upper(),
        title=title.strip(),
        description=description.strip(),
        action_type=action_type.strip() or "safe_dry_run",
        risk_level=risk_level.strip() or "low",
        payload=payload or {},
        status="pending",
        approval_scope="dry_run_only",
        execution_allowed=False,
        real_action_allowed=False,
        paid_ai_allowed=False,
        external_publish_allowed=False,
        created_at=now(),
        updated_at=now()
    )

    ledger.setdefault("requests", []).append(asdict(request))
    save_ledger(ledger)

    _event({
        "event": "approval_request_created",
        "approval_id": request.id,
        "title": request.title,
        "execution_allowed": False
    })

    return asdict(request)

def find_request(approval_id: str) -> dict | None:
    ledger = load_ledger()
    for item in ledger.get("requests", []):
        if item.get("id") == approval_id:
            return item
    return None

def approve_dry_run(approval_id: str, typed_confirmation: str) -> dict:
    ledger = load_ledger()
    target = None

    for item in ledger.get("requests", []):
        if item.get("id") == approval_id:
            target = item
            break

    if not target:
        return {
            "ok": False,
            "status": "APPROVAL_NOT_FOUND",
            "approval_id": approval_id,
            "execution_allowed": False
        }

    if typed_confirmation.strip().upper() != DRY_RUN_CONFIRMATION:
        _event({
            "event": "approval_rejected_wrong_confirmation",
            "approval_id": approval_id,
            "execution_allowed": False
        })

        return {
            "ok": False,
            "status": "APPROVAL_CONFIRMATION_INVALID",
            "required": DRY_RUN_CONFIRMATION,
            "execution_allowed": False
        }

    target["status"] = "approved_dry_run_only"
    target["approval_scope"] = "dry_run_only"
    target["execution_allowed"] = False
    target["real_action_allowed"] = False
    target["paid_ai_allowed"] = False
    target["external_publish_allowed"] = False
    target["updated_at"] = now()

    save_ledger(ledger)

    _event({
        "event": "approval_granted_dry_run_only",
        "approval_id": approval_id,
        "execution_allowed": False,
        "real_action_allowed": False
    })

    return {
        "ok": True,
        "status": "APPROVED_DRY_RUN_ONLY",
        "approval": target,
        "execution_allowed": False,
        "real_action_allowed": False,
        "paid_ai_allowed": False,
        "external_publish_allowed": False
    }

def reject_request(approval_id: str, reason: str = "") -> dict:
    ledger = load_ledger()
    target = None

    for item in ledger.get("requests", []):
        if item.get("id") == approval_id:
            target = item
            break

    if not target:
        return {
            "ok": False,
            "status": "APPROVAL_NOT_FOUND",
            "approval_id": approval_id,
            "execution_allowed": False
        }

    target["status"] = "rejected"
    target["rejection_reason"] = reason
    target["execution_allowed"] = False
    target["real_action_allowed"] = False
    target["paid_ai_allowed"] = False
    target["external_publish_allowed"] = False
    target["updated_at"] = now()

    save_ledger(ledger)

    _event({
        "event": "approval_rejected",
        "approval_id": approval_id,
        "reason": reason,
        "execution_allowed": False
    })

    return {
        "ok": True,
        "status": "APPROVAL_REJECTED",
        "approval": target,
        "execution_allowed": False
    }

def summarize_approvals() -> dict:
    ledger = load_ledger()
    requests = ledger.get("requests", [])

    return {
        "status": ledger.get("status", "READY"),
        "total": len(requests),
        "pending": len([r for r in requests if r.get("status") == "pending"]),
        "approved_dry_run_only": len([r for r in requests if r.get("status") == "approved_dry_run_only"]),
        "rejected": len([r for r in requests if r.get("status") == "rejected"]),
        "execution_allowed_count": len([r for r in requests if r.get("execution_allowed") is True]),
        "real_action_allowed_count": len([r for r in requests if r.get("real_action_allowed") is True]),
        "paid_ai_allowed_count": len([r for r in requests if r.get("paid_ai_allowed") is True]),
        "external_publish_allowed_count": len([r for r in requests if r.get("external_publish_allowed") is True]),
        "ledger_path": str(LEDGER_PATH),
        "requests": requests
    }

if __name__ == "__main__":
    req = create_approval_request(
        title="Demo Fase 39",
        description="Aprovar somente dry-run seguro. Nenhuma acao real sera executada.",
        action_type="safe_executor_bundle",
        risk_level="low",
        payload={"bundle": ["git_branch", "git_status"]}
    )
    approved = approve_dry_run(req["id"], DRY_RUN_CONFIRMATION)
    print(json.dumps({
        "created": req,
        "approved": approved,
        "summary": summarize_approvals(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

runner_code = r'''
from k_atlas.kaizen.human_approval import create_approval_request, approve_dry_run, summarize_approvals, DRY_RUN_CONFIRMATION
import json

if __name__ == "__main__":
    request = create_approval_request(
        title="Fase 39 Demo Approval",
        description="Registrar aprovacao humana dry-run para bundle seguro.",
        action_type="safe_executor_bundle",
        risk_level="low",
        payload={"actions": ["git_branch", "git_status"]}
    )

    approved = approve_dry_run(request["id"], DRY_RUN_CONFIRMATION)

    print(json.dumps({
        "status": "PHASE39_HUMAN_APPROVAL_DEMO_COMPLETED",
        "approval_id": request["id"],
        "approval_status": approved.get("status"),
        "execution_allowed": False,
        "summary": summarize_approvals(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.human_approval import (
    create_approval_request,
    approve_dry_run,
    reject_request,
    summarize_approvals,
    DRY_RUN_CONFIRMATION,
)

st.set_page_config(page_title="KOS Human Approval", layout="wide")

st.title("KOS Human Approval Console")
st.caption("Aprovacao humana auditavel. Nesta fase, aprovacao nao executa acao real.")

summary = summarize_approvals()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", summary["total"])
col2.metric("Pending", summary["pending"])
col3.metric("Approved dry-run", summary["approved_dry_run_only"])
col4.metric("Execution allowed", summary["execution_allowed_count"])

st.subheader("Criar pedido de aprovacao")
title = st.text_input("Titulo", value="Aprovar bundle seguro")
description = st.text_area("Descricao", value="Aprovar apenas dry-run. Nenhuma execucao real.")
action_type = st.selectbox("Tipo", ["safe_executor_bundle", "mission_plan", "planner_dry_run"], index=0)
risk_level = st.selectbox("Risco", ["low", "medium", "high"], index=0)

if st.button("Criar pedido", use_container_width=True):
    req = create_approval_request(
        title=title,
        description=description,
        action_type=action_type,
        risk_level=risk_level,
        payload={}
    )
    st.success(f"Pedido criado: {req['id']}")
    st.rerun()

st.subheader("Pedidos")
summary = summarize_approvals()

for req in summary.get("requests", []):
    with st.expander(f"{req.get('id')} - {req.get('title')} - {req.get('status')}"):
        st.json(req)

        typed = st.text_input(
            "Confirmacao obrigatoria",
            key="confirm_" + req.get("id"),
            value=""
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Aprovar dry-run", key="approve_" + req.get("id"), use_container_width=True):
                result = approve_dry_run(req.get("id"), typed)
                st.json(result)
                st.rerun()

        with col_b:
            if st.button("Rejeitar", key="reject_" + req.get("id"), use_container_width=True):
                result = reject_request(req.get("id"), "Rejected from UI")
                st.json(result)
                st.rerun()

st.info(f"Confirmacao para dry-run: {DRY_RUN_CONFIRMATION}")
st.warning("Esta fase nao permite publicacao, IA paga, segredo, Codex automatico ou execucao real.")
'''

test_code = r'''
from k_atlas.kaizen.human_approval import (
    create_approval_request,
    approve_dry_run,
    reject_request,
    summarize_approvals,
    DRY_RUN_CONFIRMATION,
)

def test_create_approval_request_is_safe():
    req = create_approval_request(
        title="Teste approval",
        description="Aprovar dry-run.",
        action_type="safe_executor_bundle",
        risk_level="low",
        payload={"actions": ["git_status"]}
    )
    assert req["status"] == "pending"
    assert req["execution_allowed"] is False
    assert req["real_action_allowed"] is False
    assert req["paid_ai_allowed"] is False
    assert req["external_publish_allowed"] is False

def test_wrong_confirmation_blocks_approval():
    req = create_approval_request(
        title="Teste confirmacao errada",
        description="Nao aprovar.",
        action_type="safe_executor_bundle",
        risk_level="low"
    )
    result = approve_dry_run(req["id"], "YES")
    assert result["ok"] is False
    assert result["execution_allowed"] is False

def test_approve_dry_run_does_not_allow_execution():
    req = create_approval_request(
        title="Teste approve dry-run",
        description="Aprovar apenas dry-run.",
        action_type="safe_executor_bundle",
        risk_level="low"
    )
    result = approve_dry_run(req["id"], DRY_RUN_CONFIRMATION)
    assert result["ok"] is True
    assert result["status"] == "APPROVED_DRY_RUN_ONLY"
    assert result["execution_allowed"] is False
    assert result["real_action_allowed"] is False
    assert result["paid_ai_allowed"] is False
    assert result["external_publish_allowed"] is False

def test_reject_request_blocks_execution():
    req = create_approval_request(
        title="Teste reject",
        description="Rejeitar.",
        action_type="safe_executor_bundle",
        risk_level="low"
    )
    result = reject_request(req["id"], "teste")
    assert result["ok"] is True
    assert result["status"] == "APPROVAL_REJECTED"
    assert result["execution_allowed"] is False
'''

save_json(ROOT / "config" / "kos_human_approval_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "human_approval.py", human_approval_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase39_human_approval_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Human_Approval.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase39_human_approval.py", test_code.strip() + "\n")

report = {
    "status": "PHASE39_HUMAN_APPROVAL_BOOTSTRAPPED",
    "phase": "39",
    "created_files": [
        "config/kos_human_approval_policy.json",
        "k_atlas/kaizen/human_approval.py",
        "scripts/run_phase39_human_approval_demo.py",
        "pages/KOS_Human_Approval.py",
        "tests/test_phase39_human_approval.py"
    ],
    "runtime_files": [
        "local_runtime/kaizen/human_approvals.json",
        "logs/kaizen/approvals/events.jsonl"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE39_HUMAN_APPROVAL_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))