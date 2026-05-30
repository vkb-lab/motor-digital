from __future__ import annotations

import json

from k_atlas.core.assisted_autoprogramming.kernel import AssistedAutoprogrammingKernel
from k_atlas.core.autoprogramming_proposal_reviewer.reviewer import AutoprogrammingProposalReviewer

from .builder import AutoprogrammingApplyPackageBuilder


if __name__ == "__main__":
    kernel = AssistedAutoprogrammingKernel()
    kernel.create_proposal({
        "checkpoint": "67-demo",
        "action": "create_module",
        "objective": "Criar pacote demo de aplicacao futura sem executar alteracao real.",
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
    result = builder.build_apply_packages({
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
