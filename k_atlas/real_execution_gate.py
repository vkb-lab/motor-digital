from k_atlas.real_action_guard import guard_real_action
from k_atlas.approval_package import build_approval_package
from k_atlas.live_action_receipt import create_live_action_receipt

def request_real_execution(client_id: str, platform: str, action: str, payload: dict | None = None):
    return {
        "client_id": client_id,
        "platform": platform,
        "action": action,
        "status": "PENDING_APPROVAL",
        "guard": guard_real_action(action, client_id),
        "approval_package": build_approval_package(client_id, action, payload or {}),
        "receipt": create_live_action_receipt(client_id, platform, action),
        "external_call_executed": False,
    }
