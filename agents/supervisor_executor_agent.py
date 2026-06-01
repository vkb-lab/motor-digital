def supervise_execution(job: dict):
    return {"status": "SUPERVISED", "job_id": job.get("job_id"), "client_id": job.get("client_id")}
