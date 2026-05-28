# -*- coding: utf-8 -*-
"""
K-Atlas OS - Official Boot

Ponto unico de entrada local do K-Atlas OS.

Uso:
python k_atlas_boot.py
python k_atlas_boot.py system_agent.status
python k_atlas_boot.py system_agent.agents
python k_atlas_boot.py task_agent.stats
python k_atlas_boot.py memory_agent.stats
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from agents.memory_agent import MemoryAgent
from agents.system_agent import SystemAgent
from agents.task_agent import TaskAgent
from core.kernel import KAtlasKernel, create_kernel


ROOT = Path(__file__).resolve().parent
REPORTS_DIR = ROOT / "reports"
BOOT_REPORT_FILE = REPORTS_DIR / "boot_report.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_kernel() -> KAtlasKernel:
    kernel = create_kernel(root_path=ROOT)
    kernel.start(load_state=True)

    system_agent = SystemAgent(kernel=kernel)
    kernel.register_agent(
        system_agent,
        replace=True,
        roles=["system"],
    )

    task_agent = TaskAgent(storage_path=ROOT / "memory" / "tasks.json")
    kernel.register_agent(
        task_agent,
        replace=True,
        roles=["agent"],
    )

    memory_agent = MemoryAgent(storage_path=ROOT / "memory" / "entries.json")
    kernel.register_agent(
        memory_agent,
        replace=True,
        roles=["agent"],
    )

    return kernel


def run_boot_command(kernel: KAtlasKernel, command: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    result = kernel.execute(command, payload=payload)
    return result.to_dict()


def save_boot_report(data: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BOOT_REPORT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main(argv: List[str]) -> int:
    command = argv[1] if len(argv) > 1 else "system_agent.status"
    payload: Dict[str, Any] = {}

    if len(argv) > 2:
        try:
            payload = json.loads(argv[2])
        except json.JSONDecodeError as exc:
            print("Payload JSON invalido:", str(exc))
            return 2

    kernel = build_kernel()

    try:
        result = run_boot_command(kernel, command, payload)

        report = {
            "app": "K-Atlas OS",
            "entrypoint": "k_atlas_boot.py",
            "created_at": now_iso(),
            "success": bool(result.get("success")),
            "command": command,
            "payload": payload,
            "result": result,
            "kernel_status": kernel.status(),
        }

        save_boot_report(report)

        print("K-Atlas OS boot OK")
        print("Command:", command)
        print("Success:", report["success"])
        print("Report:", BOOT_REPORT_FILE)

        if not report["success"]:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1

        return 0

    finally:
        kernel.stop(save_state=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
