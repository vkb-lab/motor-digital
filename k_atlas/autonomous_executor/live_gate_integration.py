from k_atlas.live_onboarding.readiness_matrix import build_readiness_matrix
from k_atlas.real_execution_gate import request_real_execution

def attach_live_gate_preview(result: dict):
    client_id = result.get("client_id", "parada_atlantida")
    result["live_connector_readiness"] = build_readiness_matrix(client_id)
    result["live_gate"] = request_real_execution(client_id, "instagram", "publish_instagram", {"source": "phase7_preview"})
    result["status"] = "PENDING_FINAL_APPROVAL"
    return result
