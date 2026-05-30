from __future__ import annotations

import json

from k_atlas.core.assisted_autoprogramming.kernel import AssistedAutoprogrammingKernel

from .reviewer import AutoprogrammingProposalReviewer


if __name__ == "__main__":
    kernel = AssistedAutoprogrammingKernel()
    kernel.create_proposal({
        "checkpoint": "66-demo",
        "action": "create_module",
        "objective": "Criar uma proposta demo para revisao supervisionada.",
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
    })

    reviewer = AutoprogrammingProposalReviewer()
    result = reviewer.build_review_queue()
    print(json.dumps(result, ensure_ascii=False, indent=2))
