from __future__ import annotations

import json

from .orchestrator import AssistedAutonomyOrchestrator


def main() -> int:
    result = AssistedAutonomyOrchestrator().run(requested_by="checkpoint_40")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
