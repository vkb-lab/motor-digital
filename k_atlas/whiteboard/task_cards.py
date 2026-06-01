def create_task_cards(tasks: list):
    return [
        {
            "task_id": task["task_id"],
            "title": task.get("title", task["task_id"]),
            "status": task.get("status", "PENDING_APPROVAL"),
            "agent": task.get("agent", "SystemAgent"),
        }
        for task in tasks
    ]
