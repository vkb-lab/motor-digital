def build_board(job: dict):
    return {
        "status": "WHITEBOARD_READY",
        "job_id": job["job_id"],
        "client_id": job["client_id"],
        "cards": [
            {
                "task_id": task["task_id"],
                "title": task["title"],
                "agent": task["agent"],
                "status": task["status"],
                "approval_required": True,
            }
            for task in job.get("tasks", [])
        ],
    }
