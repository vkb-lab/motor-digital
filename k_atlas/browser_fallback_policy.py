def browser_fallback(task_id: str):
    return {
        "task_id": task_id,
        "status": "BROWSER_MANUAL_BRIDGE_READY",
        "real_browser_action_allowed": False,
        "manual_approval_required": True,
    }
