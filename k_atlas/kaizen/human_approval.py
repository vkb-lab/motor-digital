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
