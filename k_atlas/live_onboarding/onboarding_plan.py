from k_atlas.live_onboarding.platform_requirements import get_requirements

def build_onboarding_plan(client_id: str, platform: str):
    return {
        "client_id": client_id,
        "platform": platform,
        "status": "PENDING_APPROVAL",
        "requirements": get_requirements(platform),
        "steps": [
            "validar conta",
            "configurar env local",
            "rodar readiness",
            "gerar approval package",
        ],
        "real_actions_enabled": False,
    }
