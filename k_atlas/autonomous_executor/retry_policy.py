def should_retry(task: dict, attempts: int = 0):
    return attempts < 1 and task.get("status") == "FAILED"
