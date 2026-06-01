def choose_api_first(task_id: str):
    api_tasks = ["instagram_post", "publication_queue", "google_business", "meta_ads"]
    return {
        "task_id": task_id,
        "preferred_channel": "API_DRY_RUN" if task_id in api_tasks else "LOCAL",
        "real_api_call_allowed": False,
    }
