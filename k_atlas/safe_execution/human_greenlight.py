from datetime import datetime, timezone

def build_human_decision(client_id: str, campaign_name: str, decision: str = "OK"):
    allowed = str(decision).strip().upper() == "OK"
    return {
        "status": "HUMAN_OK" if allowed else "HUMAN_REVIEW_NEEDED",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "decision": decision,
        "safe_execution_allowed": allowed,
        "real_actions_enabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
