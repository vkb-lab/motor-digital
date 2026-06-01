SENSITIVE_ACTIONS = ["publish_instagram","send_dm","create_ad","edit_google_business","charge_payment","deploy_production"]

def classify_action(action: str):
    sensitive = action in SENSITIVE_ACTIONS or str(action).startswith("real_")
    return {"action": action, "sensitive": sensitive, "requires_manual_approval": sensitive}
