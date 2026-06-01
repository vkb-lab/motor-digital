from k_atlas.launch_sandbox.launch_plan import build_launch_plan
from k_atlas.launch_sandbox.channel_preview import build_channel_previews
from k_atlas.launch_sandbox.asset_pack import build_asset_pack
from k_atlas.launch_sandbox.confirmation_package import build_confirmation_package
from k_atlas.launch_sandbox.client_launch_board import build_client_launch_board

def run_launch_sandbox(client_id: str = "parada_atlantida", campaign_name: str = "campanha_lancamento_parada_atlantida", objective: str = "lancamento"):
    plan = build_launch_plan(client_id, campaign_name, objective)
    previews = build_channel_previews(plan)
    asset_pack = build_asset_pack(plan, previews)
    confirmation = build_confirmation_package(client_id, campaign_name, asset_pack)
    board = build_client_launch_board(confirmation)

    return {
        "status": "PENDING_FINAL_APPROVAL",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "plan": plan,
        "previews": previews,
        "asset_pack": asset_pack,
        "confirmation": confirmation,
        "board": board,
        "real_actions_enabled": False,
        "real_action_executed": False,
        "manual_approval_required": True,
    }
