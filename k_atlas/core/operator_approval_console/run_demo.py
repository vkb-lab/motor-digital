from __future__ import annotations

import json
from .console import OperatorApprovalConsole

if __name__ == "__main__":
    console = OperatorApprovalConsole()
    item = console.create_request({
        "action_type": "mission_install",
        "title": "Demo approval request",
        "description": "Solicitacao demo sem execucao automatica.",
        "auto_execute": False,
        "real_execution_enabled": False,
    })
    print(json.dumps(item, ensure_ascii=False, indent=2))
