from datetime import datetime, timezone

def build_media_request(client_id: str, campaign_name: str, image_url: str, caption: str):
    return {
        "status": "MEDIA_REQUEST_READY",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "image_url": image_url,
        "caption": caption,
        "media_type": "IMAGE",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
