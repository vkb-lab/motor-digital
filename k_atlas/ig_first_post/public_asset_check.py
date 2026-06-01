def inspect_public_asset(image_url: str):
    valid = isinstance(image_url, str) and image_url.startswith("https://") and len(image_url) > 12
    return {
        "status": "ASSET_URL_READY" if valid else "ASSET_URL_INVALID",
        "image_url": image_url,
        "is_https": str(image_url).startswith("https://"),
        "network_call_executed": False,
    }
