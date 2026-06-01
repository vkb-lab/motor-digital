def assign_agent(task: dict):
    return {
        "task_id": task["task_id"],
        "agent": task.get("agent", "SystemAgent"),
        "status": "ASSIGNED",
    }
