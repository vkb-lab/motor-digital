from datetime import datetime, timezone

def build_first_post_spec(
    client_id: str = "parada_atlantida",
    campaign_name: str = "campanha_lancamento_parada_atlantida",
    image_url: str = "https://placehold.co/1080x1080/png",
    caption: str = "Primeiro teste controlado preparado pelo K-OS."
):
    return {
        "status": "FIRST_POST_SPEC_READY",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "image_url": image_url,
        "caption": caption,
        "format": "IMAGE",
        "manual_review_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
