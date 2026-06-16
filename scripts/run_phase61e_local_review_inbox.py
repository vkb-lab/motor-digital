from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.local_review_inbox import collect_review_inbox

if __name__ == "__main__":
    result = collect_review_inbox(limit=20)

    print(json.dumps({
        "status": "PHASE61E_LOCAL_REVIEW_INBOX_COMPLETED",
        "result_status": result.get("status"),
        "summary": result.get("summary"),
        "read_only": True,
        "execute_allowed_now": False,
        "repo_write_allowed_now": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))