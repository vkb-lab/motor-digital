from pathlib import Path

def validate_artifacts(artifacts: dict):
    required = ["campaign", "landing_page", "qr_code", "instagram_post", "creative", "publication_queue"]
    items = artifacts.get("items", {})
    missing = [item for item in required if item not in items]
    return {
        "status": "VALID" if not missing else "MISSING_ARTIFACTS",
        "missing": missing,
        "path_exists": Path(artifacts.get("path", "")).exists() if artifacts.get("path") else False,
    }
