# -*- coding: utf-8 -*-
"""
Smoke test do boot oficial do K-Atlas OS.

Uso:
python smoke_test_boot.py
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

    print(completed.stdout)

    if completed.stderr:
        print(completed.stderr)

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    run([sys.executable, "k_atlas_boot.py"])
    run([sys.executable, "k_atlas_boot.py", "system_agent.ping"])
    run([sys.executable, "k_atlas_boot.py", "system_agent.agents"])
    run([sys.executable, "k_atlas_boot.py", "task_agent.ping"])
    run([sys.executable, "k_atlas_boot.py", "task_agent.stats"])
    run([sys.executable, "k_atlas_boot.py", "memory_agent.ping"])
    run([sys.executable, "k_atlas_boot.py", "memory_agent.stats"])
    run([sys.executable, "k_atlas_boot.py", "orchestrator_agent.ping"])
    run([sys.executable, "k_atlas_boot.py", "orchestrator_agent.status"])
    print("Smoke test boot OK")
