def build_final_approval(result: dict):
    return {"status": "PENDING_APPROVAL", "manual_approval_required": True, "result": result}
