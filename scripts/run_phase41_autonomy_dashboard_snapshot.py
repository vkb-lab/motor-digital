from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot
import json

if __name__ == "__main__":
    snapshot = build_autonomy_snapshot(write_log=True)
    print(json.dumps({
        "status": "PHASE41_AUTONOMY_DASHBOARD_SNAPSHOT_COMPLETED",
        "branch": snapshot.get("git", {}).get("branch"),
        "git_dirty": bool(snapshot.get("git", {}).get("status_short", "").strip()),
        "codex_installed": snapshot.get("tools", {}).get("codex", {}).get("installed"),
        "ollama_installed": snapshot.get("tools", {}).get("ollama", {}).get("installed"),
        "production_publish_locked": snapshot.get("runtime_locks", {}).get("production_publish_locked"),
        "paid_ai_locked": snapshot.get("runtime_locks", {}).get("paid_ai_locked"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
