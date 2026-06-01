def collect_results(job: dict, artifacts: dict, receipts: list, final_review: dict):
    return {
        "status": "PENDING_FINAL_APPROVAL",
        "client_id": job["client_id"],
        "job_id": job["job_id"],
        "job": job,
        "artifacts": artifacts,
        "receipts": receipts,
        "final_review": final_review,
        "external_call_executed": False,
    }
