def audit_quality(result: dict):
    return {"status": "AUDITED", "result_status": result.get("status"), "issues": []}
