DEFAULT_CHANNELS = [
    "instagram",
    "facebook_page",
    "meta_ads",
    "google_business",
    "whatsapp_business",
    "landing_page",
    "qr_code",
]

def build_launch_plan(client_id: str, campaign_name: str, objective: str = "lancamento", channels=None):
    selected_channels = channels or DEFAULT_CHANNELS
    return {
        "status": "PENDING_APPROVAL",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "objective": objective,
        "channels": selected_channels,
        "real_actions_enabled": False,
        "manual_approval_required": True,
        "steps": [
            "preparar campanha",
            "montar previews por canal",
            "gerar pacote de aprovacao",
            "aguardar confirmacao humana",
        ],
    }
