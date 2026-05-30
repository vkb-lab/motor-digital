from __future__ import annotations

import json

from .factory_workflow import SaaSFactoryWorkflowRunner
from .workflow_spec import build_default_saas_workflow_payload


def main() -> int:
    result = SaaSFactoryWorkflowRunner().run(
        payload=build_default_saas_workflow_payload(),
        requested_by="checkpoint_38",
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
