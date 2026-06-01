from datetime import datetime, timezone

def execute_safe_channel_task(task: dict):
    return {
        "status": "SAFE_EXECUTED",
        "task_id": task["id"],
        "client_id": task["client_id"],
        "campaign_name": task["campaign_name"],
        "channel": task["channel"],
        "mode": "SANDBOX_EXECUTION",
        "external_call_executed": False,
        "real_action_executed": False,
        "manual_review_required": True,
        "result": f"Sandbox execution prepared for {task['channel']}",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
