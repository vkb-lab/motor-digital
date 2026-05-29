from __future__ import annotations

import json

from .autopilot import SupervisorAutopilot


def main() -> int:
    result = SupervisorAutopilot().run_once()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
