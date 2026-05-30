from __future__ import annotations

import json

from k_atlas.core.publish_approval_gate.gate import SecurePublishApprovalGate

from .stub import ExternalActionExecutionStub


if __name__ == "__main__":
    gate = SecurePublishApprovalGate()
    request = gate.create_request()
    gate.decide(
        request_id=request["request_id"],
        decision="approved",
        reviewer="k_atlas_operator",
        notes="Aprovado para stub. Sem execução externa.",
    )

    result = ExternalActionExecutionStub(approval_gate=gate).execute_approved_stubs()
    print(json.dumps(result, ensure_ascii=False, indent=2))
