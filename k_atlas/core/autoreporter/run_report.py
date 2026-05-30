from __future__ import annotations

import json

from .report_builder import AutoReporterCentral


def main() -> int:
    result = AutoReporterCentral().generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
