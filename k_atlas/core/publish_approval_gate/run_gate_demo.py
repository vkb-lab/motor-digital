from __future__ import annotations

import json

from .gate import SecurePublishApprovalGate


if __name__ == "__main__":
    gate = SecurePublishApprovalGate()
    request = gate.create_request()
    decision = gate.decide(
        request_id=request["request_id"],
        decision="approved",
        reviewer="k_atlas_operator",
        notes="Aprovação registrada apenas para teste. Sem execução externa.",
    )
    report = gate.save_report()
    print(json.dumps({"request": request, "decision": decision, "report": report}, ensure_ascii=False, indent=2))
