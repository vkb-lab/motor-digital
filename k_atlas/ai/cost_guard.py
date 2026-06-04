from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import uuid

ROOT = Path(__file__).resolve().parents[2]
BUDGET_PATH = ROOT / "config" / "ai_budget_policy.json"
LEDGER_PATH = ROOT / "logs" / "ai_cost" / "ledger.jsonl"

@dataclass
class CostDecision:
    allowed: bool
    blocked: bool
    reason: str
    provider: str
    estimated_usd: float
    request_id: str

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_budget() -> dict:
    if BUDGET_PATH.exists():
        return json.loads(BUDGET_PATH.read_text(encoding="utf-8-sig"))
    return {
        "mode": "DEV_SAFE",
        "default_provider": "local_stub",
        "per_request_max_usd": 0.05,
        "hard_blocks": {
            "gemini": True,
            "openai": True,
            "anthropic": True,
            "browser_logged_accounts": True
        },
        "allow": {
            "local_stub": True
        },
        "rules": {
            "require_client_id": True,
            "require_task_id": True,
            "require_cost_estimate": True,
            "require_ledger_log": True
        }
    }

def log_ledger(event: dict) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def check_cost_gate(
    provider: str,
    client_id: str,
    task_id: str,
    estimated_usd: float = 0.0,
    model: str = ""
) -> CostDecision:
    budget = load_budget()
    request_id = str(uuid.uuid4())

    provider_key = (provider or budget.get("default_provider") or "local_stub").strip()
    hard_blocks = budget.get("hard_blocks", {})
    allow = budget.get("allow", {})
    rules = budget.get("rules", {})

    allowed = True
    reason = "allowed"

    if rules.get("require_client_id", True) and not client_id:
        allowed = False
        reason = "client_id obrigatorio"

    if rules.get("require_task_id", True) and not task_id:
        allowed = False
        reason = "task_id obrigatorio"

    if hard_blocks.get(provider_key, False):
        allowed = False
        reason = f"provider bloqueado por politica: {provider_key}"

    if not allow.get(provider_key, False):
        allowed = False
        reason = f"provider nao habilitado: {provider_key}"

    per_request_max = float(budget.get("per_request_max_usd", 0.05))
    if float(estimated_usd or 0.0) > per_request_max:
        allowed = False
        reason = f"estimativa acima do limite por requisicao: {estimated_usd} > {per_request_max}"

    decision = CostDecision(
        allowed=allowed,
        blocked=not allowed,
        reason=reason,
        provider=provider_key,
        estimated_usd=float(estimated_usd or 0.0),
        request_id=request_id
    )

    log_ledger({
        "request_id": request_id,
        "created_at": _now(),
        "event": "cost_gate_check",
        "provider": provider_key,
        "model": model,
        "client_id": client_id,
        "task_id": task_id,
        "estimated_usd": float(estimated_usd or 0.0),
        "decision": asdict(decision)
    })

    return decision
