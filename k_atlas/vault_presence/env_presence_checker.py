import os
from k_atlas.live_onboarding.platform_requirements import get_requirements

def _check_platform_env(platform: str):
    required = get_requirements(platform)
    missing = [name for name in required if not os.getenv(name)]
    return {
        "platform": platform,
        "status": "READY_DRY_RUN" if not missing else "MISSING_ENV",
        "missing": missing,
        "values_exposed": False,
        "values_saved": False,
        "real_actions_enabled": False,
    }

def check_env_presence(platform: str):
    return _check_platform_env(platform)

def check_token_presence(platform: str):
    return _check_platform_env(platform)
