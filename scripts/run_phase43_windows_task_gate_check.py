from k_atlas.kaizen.windows_task_gate import build_registration_plan, check_windows_task_status
import json

if __name__ == "__main__":
    print(json.dumps({
        "status": "PHASE43_WINDOWS_TASK_GATE_CHECK_COMPLETED",
        "plan": build_registration_plan(),
        "task_status": check_windows_task_status(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
