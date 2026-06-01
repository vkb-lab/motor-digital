from pathlib import Path
import json
from datetime import datetime, timezone
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(value: str) -> str:
    return str(value or "demo").lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def _write_json(path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data


def generate_local_creative(
    client_id: str = "parada_atlantida",
    campaign_id: str = "demo",
    style: str = "clean_premium",
) -> Dict[str, Any]:
    output_dir = ROOT / "reports" / "creative_outputs"
    data = {
        "status": "PENDING_APPROVAL",
        "client_id": client_id,
        "campaign_id": campaign_id,
        "style": style,
        "created_at": utc_now(),
        "assets": ["image_prompt", "video_prompt", "reels_plan", "thumbnail_plan"],
        "manual_approval_required": True,
        "external_call_executed": False,
    }
    return _write_json(output_dir / f"{_safe(client_id)}_{_safe(campaign_id)}_creative_package.json", data)


def create_image_asset(
    client_id: str = "parada_atlantida",
    campaign_id: str = "demo",
    style: str = "clean_premium",
    text: str = "Parada Atlantida",
) -> Dict[str, Any]:
    output_dir = ROOT / "reports" / "media_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image, ImageDraw

        image_path = output_dir / f"{_safe(client_id)}_{_safe(campaign_id)}_{_safe(style)}.png"
        img = Image.new("RGB", (1080, 1080), "white")
        draw = ImageDraw.Draw(img)
        draw.text((80, 120), text, fill="black")
        draw.text((80, 180), f"Style: {style}", fill="black")
        draw.text((80, 240), "Status: PENDING_APPROVAL", fill="black")
        img.save(image_path)

        return {
            "status": "PENDING_APPROVAL",
            "generation_status": "CREATED",
            "client_id": client_id,
            "campaign_id": campaign_id,
            "style": style,
            "output_type": "image",
            "path": str(image_path),
            "manual_approval_required": True,
            "external_call_executed": False,
        }
    except Exception:
        fallback_path = output_dir / f"{_safe(client_id)}_{_safe(campaign_id)}_{_safe(style)}_image_plan.json"
        data = {
            "status": "FALLBACK_IMAGE_PLAN",
            "client_id": client_id,
            "campaign_id": campaign_id,
            "style": style,
            "output_type": "image_plan",
            "prompt": text,
            "manual_approval_required": True,
            "external_call_executed": False,
        }
        return _write_json(fallback_path, data)


def create_video_recipe(
    client_id: str = "parada_atlantida",
    campaign_id: str = "demo",
    style: str = "cinematic_travel",
) -> Dict[str, Any]:
    output_dir = ROOT / "reports" / "media_outputs"
    data = {
        "status": "FALLBACK_VIDEO_PLAN",
        "mode": "FALLBACK_VIDEO_PLAN",
        "client_id": client_id,
        "campaign_id": campaign_id,
        "style": style,
        "output_type": "video_recipe",
        "created_at": utc_now(),
        "scenes": [
            {"scene": 1, "title": "Gancho inicial", "description": "Mostrar uma experiencia local com chamada rapida.", "duration_seconds": 3},
            {"scene": 2, "title": "Experiencia", "description": "Apresentar turismo, gastronomia ou cupom.", "duration_seconds": 6},
            {"scene": 3, "title": "CTA", "description": "Chamar para QR Code, landing page ou direct.", "duration_seconds": 4}
        ],
        "manual_approval_required": True,
        "external_call_executed": False,
    }
    return _write_json(output_dir / f"{_safe(client_id)}_{_safe(campaign_id)}_{_safe(style)}_video_recipe.json", data)


def create_creative_package(
    client_id: str = "parada_atlantida",
    campaign_id: str = "demo",
    style: str = "clean_premium",
) -> Dict[str, Any]:
    creative = generate_local_creative(client_id, campaign_id, style)
    image = create_image_asset(client_id, campaign_id, style)
    video = create_video_recipe(client_id, campaign_id, style)

    data = {
        "status": "PENDING_APPROVAL",
        "client_id": client_id,
        "campaign_id": campaign_id,
        "style": style,
        "created_at": utc_now(),
        "creative_package": creative,
        "image": image,
        "video": video,
        "image_asset": image,
        "video_recipe": video,
        "manual_approval_required": True,
        "external_call_executed": False,
    }

    client_campaign_dir = ROOT / "clients" / client_id / "campaigns"
    return _write_json(client_campaign_dir / f"{_safe(campaign_id)}_creative_package.json", data)


def create_campaign_creative(
    client_id: str = "parada_atlantida",
    campaign_id: str = "demo",
    style: str = "clean_premium",
    objective: str = "campanha promocional",
) -> Dict[str, Any]:
    result = create_creative_package(client_id, campaign_id, style)
    result["objective"] = objective
    result["status"] = "PENDING_APPROVAL"
    result["approval_status"] = "PENDING_APPROVAL"

    if "image" not in result and "image_asset" in result:
        result["image"] = result["image_asset"]

    if "video" not in result and "video_recipe" in result:
        result["video"] = result["video_recipe"]

    return result
