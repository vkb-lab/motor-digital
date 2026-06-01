def generate_env_manifest(client_id: str, platforms: list):
    return {
        "client_id": client_id,
        "platforms": platforms,
        "values_saved": False,
        "status": "SAFE_MANIFEST",
    }
