from k_atlas.sensitive_action_policy import classify_action

def guard_real_action(action: str, client_id: str = "parada_atlantida"):
    policy = classify_action(action)
    return {
        "client_id": client_id,
        "action": action,
        "allowed": False,
        "status": "PENDING_APPROVAL" if policy["requires_manual_approval"] else "DRY_RUN_ALLOWED",
        "manual_approval_required": policy["requires_manual_approval"],
        "external_call_executed": False,
    }
