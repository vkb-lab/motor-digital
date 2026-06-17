from __future__ import annotations

from k_atlas.kaizen.queue_approval_executor import process_approvals


if __name__ == "__main__":
    status = process_approvals(limit=5)
    import json
    print(json.dumps(status, indent=2, ensure_ascii=False))
