from __future__ import annotations

import json

from k_atlas.core.assisted_autoprogramming.kernel import AssistedAutoprogrammingKernel
from k_atlas.core.autoprogramming_proposal_reviewer.reviewer import AutoprogrammingProposalReviewer
from k_atlas.core.autoprogramming_apply_package_builder.builder import AutoprogrammingApplyPackageBuilder

from .gate import AutoprogrammingApplyPackageGate


if __name__ == "__main__":
    kernel = AssistedAutoprogrammingKernel()
    kernel.create_proposal({
        "checkpoint": "68-demo",
        "action": "create_module",
        "objective": "Criar pacote demo para validacao no gate.",
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
    })

    reviewer = AutoprogrammingProposalReviewer()
    review_result = reviewer.build_review_queue()

    for item in review_result.get("created_reviews", []):
        reviewer.decide(
            review_id=item["review_id"],
            decision="approve_for_apply_package",
            reviewer="k_atlas_operator",
            notes="aprovacao demo supervisionada",
        )

    builder = AutoprogrammingApplyPackageBuilder()
    builder.build_apply_packages()

    gate = AutoprogrammingApplyPackageGate()
    result = gate.build_gate_queue()

    print(json.dumps(result, ensure_ascii=False, indent=2))
