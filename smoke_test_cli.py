# -*- coding: utf-8 -*-
"""
Smoke test da CLI do K-Atlas OS.

Uso:
python smoke_test_cli.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )

    print("COMMAND:", " ".join(command))
    print(completed.stdout)

    if completed.stderr:
        print(completed.stderr)

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    run([sys.executable, "k_atlas_cli.py", "status"])
    run([sys.executable, "k_atlas_cli.py", "agents"])
    run([sys.executable, "k_atlas_cli.py", "task-stats"])
    run([sys.executable, "k_atlas_cli.py", "memory-stats"])
    run([sys.executable, "k_atlas_cli.py", "orchestrator-status"])
    run([sys.executable, "k_atlas_cli.py", "run", "system_agent.ping"])
    run([sys.executable, "k_atlas_cli.py", "run", "orchestrator_agent.ping"])
    print("Smoke test CLI OK")
