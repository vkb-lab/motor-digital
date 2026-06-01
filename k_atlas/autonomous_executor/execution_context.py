from k_atlas.multiclient_registry import resolve_client_id

def build_execution_context(command: str):
    client_id = resolve_client_id(command)
    return {
        "client_id": client_id,
        "command": command,
        "dry_run": True,
        "manual_approval_required": True,
    }
