DEFAULT_CHANNELS = [
    "instagram",
    "facebook_page",
    "meta_ads",
    "google_business",
    "whatsapp_business",
    "landing_page",
    "qr_code",
]

def build_channel_queue(client_id: str, campaign_name: str, channels=None):
    queue = []
    for index, channel in enumerate(channels or DEFAULT_CHANNELS, start=1):
        queue.append({
            "id": f"safe_task_{index:02d}_{channel}",
            "client_id": client_id,
            "campaign_name": campaign_name,
            "channel": channel,
            "status": "READY_FOR_SAFE_EXECUTION",
            "mode": "SANDBOX_EXECUTION",
            "real_action_executed": False,
            "manual_review_required": True,
        })
    return {
        "status": "QUEUE_READY",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "items": queue,
        "real_actions_enabled": False,
    }
