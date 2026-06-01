from k_atlas.live_onboarding.platform_registry import PLATFORMS
from k_atlas.vault_presence.env_presence_checker import check_env_presence

def build_readiness_matrix(client_id: str):
    platforms = {}
    for platform in PLATFORMS:
        data = check_env_presence(platform)
        data["client_id"] = client_id
        data["manual_approval_required"] = True
        platforms[platform] = data
    return {
        "client_id": client_id,
        "status": "READY_DRY_RUN",
        "platforms": platforms,
        "real_actions_enabled": False,
        "manual_approval_required": True,
    }
