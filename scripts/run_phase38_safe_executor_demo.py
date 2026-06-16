from k_atlas.kaizen.safe_executor import run_phase38_smoke, list_safe_actions
import json

if __name__ == "__main__":
    result = run_phase38_smoke()
    print(json.dumps({
        "status": "PHASE38_SAFE_EXECUTOR_DEMO_COMPLETED",
        "allowed_actions": list_safe_actions(),
        "result": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
