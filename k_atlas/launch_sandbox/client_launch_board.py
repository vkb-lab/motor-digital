def build_client_launch_board(confirmation: dict):
    asset_pack = confirmation.get("asset_pack", {})
    previews = asset_pack.get("previews", {})
    cards = []

    for channel, preview in previews.items():
        cards.append({
            "id": channel,
            "title": f"Preview {channel}",
            "status": preview.get("status", "PENDING_APPROVAL"),
            "real_action_executed": False,
            "manual_approval_required": True,
        })

    return {
        "status": "LAUNCH_BOARD_READY",
        "client_id": confirmation["client_id"],
        "campaign_name": confirmation["campaign_name"],
        "cards": cards,
        "real_actions_enabled": False,
    }
