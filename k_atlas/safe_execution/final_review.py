from datetime import datetime, timezone

def build_safe_execution_review(client_id: str, campaign_name: str, decision: dict, queue: dict, receipts: dict):
    return {
        "status": "SAFE_EXECUTION_REVIEW_READY",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "decision": decision,
        "queue_status": queue.get("status"),
        "receipts_status": receipts.get("status"),
        "total_tasks": len(queue.get("items", [])),
        "real_action_executed": False,
        "external_call_executed": False,
        "next_step": "Fase 10 pode conectar credenciais reais e executar publicacao controlada por canal.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
