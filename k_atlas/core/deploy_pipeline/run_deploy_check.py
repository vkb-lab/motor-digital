from __future__ import annotations

import json

from .pipeline import DeployPipelineAssistant


def main() -> int:
    result = DeployPipelineAssistant().run_assisted_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("validation", {}).get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
