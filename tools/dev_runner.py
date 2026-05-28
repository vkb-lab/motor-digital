# -*- coding: utf-8 -*-
"""
K-Atlas OS - Local Dev Runner

Executor local para validar o estado do projeto.
Compativel com Windows / PowerShell / UTF-8.

Uso:
python tools/dev_runner.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORT_FILE = REPORTS_DIR / "dev_runner_report.json"


COMMANDS = [
    {
        "name": "smoke_test_kernel",
        "cmd": [sys.executable, "smoke_test_kernel.py"],
        "required": True,
    },
    {
        "name": "smoke_test_system_agent",
        "cmd": [sys.executable, "smoke_test_system_agent.py"],
        "required": True,
    },
    {
        "name": "smoke_test_task_agent",
        "cmd": [sys.executable, "smoke_test_task_agent.py"],
        "required": True,
    },
    {
        "name": "smoke_test_memory_agent",
        "cmd": [sys.executable, "smoke_test_memory_agent.py"],
        "required": True,
    },
    {
        "name": "smoke_test_boot",
        "cmd": [sys.executable, "smoke_test_boot.py"],
        "required": True,
    },
    {
        "name": "smoke_test_cli",
        "cmd": [sys.executable, "smoke_test_cli.py"],
        "required": True,
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(item: Dict[str, Any]) -> Dict[str, Any]:
    started_at = now_iso()

    try:
        completed = subprocess.run(
            item["cmd"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )

        return {
            "name": item["name"],
            "cmd": item["cmd"],
            "required": item.get("required", False),
            "success": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "started_at": started_at,
            "finished_at": now_iso(),
        }

    except Exception as exc:
        return {
            "name": item["name"],
            "cmd": item["cmd"],
            "required": item.get("required", False),
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "started_at": started_at,
            "finished_at": now_iso(),
        }


def git_status() -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        return {
            "available": completed.returncode == 0,
            "returncode": completed.returncode,
            "output": completed.stdout.strip(),
            "error": completed.stderr.strip(),
        }

    except Exception as exc:
        return {
            "available": False,
            "returncode": None,
            "output": "",
            "error": str(exc),
        }


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    failed_required = []

    print("K-Atlas OS - Local Dev Runner")
    print("Root:", ROOT)
    print("Started:", now_iso())
    print("")

    for item in COMMANDS:
        print("Running:", item["name"])
        result = run_command(item)
        results.append(result)

        if result["success"]:
            print("OK:", item["name"])
        else:
            print("FAIL:", item["name"])
            print(result["stderr"])

        if item.get("required", False) and not result["success"]:
            failed_required.append(item["name"])

        print("")

    report = {
        "app": "K-Atlas OS",
        "runner": "local_dev_runner",
        "created_at": now_iso(),
        "root": str(ROOT),
        "success": len(failed_required) == 0,
        "failed_required": failed_required,
        "commands": results,
        "git_status": git_status(),
    }

    REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Report saved:", REPORT_FILE)

    if report["success"]:
        print("K-Atlas validation: OK")
        return 0

    print("K-Atlas validation: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
