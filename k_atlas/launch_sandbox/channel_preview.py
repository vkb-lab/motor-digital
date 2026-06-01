def build_channel_previews(plan: dict):
    campaign_name = plan["campaign_name"]
    client_id = plan["client_id"]
    previews = {}

    for channel in plan["channels"]:
        previews[channel] = {
            "status": "PENDING_APPROVAL",
            "mode": "SANDBOX_PREVIEW",
            "client_id": client_id,
            "campaign_name": campaign_name,
            "headline": f"{campaign_name} - preview {channel}",
            "caption": f"Preview controlado para {client_id}. Nenhuma acao real executada.",
            "cta": "Aguardando aprovacao final",
            "real_action_executed": False,
            "manual_approval_required": True,
        }

    return previews
