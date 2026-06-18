from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.autonomous_job_runner import process_inbox

def main() -> int:
    parser = argparse.ArgumentParser(description="K-OS Autonomous Job Runner")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    payload = process_inbox(limit=args.limit)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
