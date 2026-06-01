from k_atlas.api_first_policy import choose_api_first
from k_atlas.browser_fallback_policy import browser_fallback

def route_action_channel(task_id: str):
    api = choose_api_first(task_id)
    if api["preferred_channel"] == "API_DRY_RUN":
        return {
            "task_id": task_id,
            "channel": "API_DRY_RUN",
            "external_call_executed": False,
            "status": "PENDING_APPROVAL",
        }
    return browser_fallback(task_id)
