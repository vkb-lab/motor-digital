from __future__ import annotations

import json

from .runner import MissionPipelineRunner


if __name__ == "__main__":
    runner = MissionPipelineRunner()
    report = runner.dry_run({"mode": "dry_run"})
    print(json.dumps(report, ensure_ascii=False, indent=2))
