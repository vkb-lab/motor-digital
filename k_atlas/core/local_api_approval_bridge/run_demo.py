from __future__ import annotations

import json

from .bridge import LocalApiApprovalBridge


if __name__ == "__main__":
    bridge = LocalApiApprovalBridge()
    bridge.create_request({
        "source": "demo",
        "intent": "test_approval_queue",
        "action": "no_op",
    })
    print(json.dumps(bridge.summary(), ensure_ascii=False, indent=2, sort_keys=True))
