def route_operation(task: dict):
    task_id = task.get("task_id", "")
    channel = "LOCAL_DRY_RUN"
    if task_id in ["instagram_post", "publication_queue"]:
        channel = "API_DRY_RUN"
    if task_id in ["landing_page", "qr_code", "creative"]:
        channel = "LOCAL_ARTIFACT"
    return {
        "task_id": task_id,
        "channel": channel,
        "external_call_executed": False,
        "status": "ROUTED",
    }
