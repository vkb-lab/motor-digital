from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = PROJECT_ROOT / "reports" / "autonomy"
REPORT_JSON = REPORT_DIR / "autonomy_ladder_status.json"
REPORT_MD = REPORT_DIR / "autonomy_ladder_status.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(command: list[str], timeout: int = 180) -> dict[str, Any]:
    started_at = utc_now_iso()

    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

        return {
            "ok": completed.returncode == 0,
            "command": " ".join(command),
            "returncode": completed.returncode,
            "started_at": started_at,
            "finished_at": utc_now_iso(),
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-8000:],
        }

    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "command": " ".join(command),
            "returncode": None,
            "started_at": started_at,
            "finished_at": utc_now_iso(),
            "stdout": (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-8000:] if isinstance(exc.stderr, str) else "",
            "error": "timeout",
        }


def file_exists(path: str) -> bool:
    return (PROJECT_ROOT / path).exists()


def count_dirs(path: str) -> int:
    root = PROJECT_ROOT / path
    if not root.exists():
        return 0
    return len([item for item in root.iterdir() if item.is_dir()])


def build_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    checks = {
        "control_plane_module": file_exists("k_atlas/core/control_plane/task_router.py"),
        "control_plane_executor": file_exists("k_atlas/core/control_plane/executor.py"),
        "workflows_module": file_exists("k_atlas/core/workflows/workflow_runner.py"),
        "blackboard_module": file_exists("k_atlas/core/blackboard/powershell_runner.py"),
        "social_audit_module": file_exists("k_atlas/social/social_audit/profile_audit.py"),
        "social_audit_live_status": file_exists("k_atlas/social/social_audit/live_status.py"),
        "blackboard_runner_script": file_exists("ops/start_blackboard_runner.ps1"),
        "social_audit_reports_count": count_dirs("reports/social_audit"),
    }

    passed_commands = len([item for item in results if item["ok"]])
    failed_commands = len([item for item in results if not item["ok"]])

    autonomy_level = "level_3_assisted_execution"

    if failed_commands > 0:
        autonomy_level = "level_2_needs_fix"

    if (
        checks["control_plane_module"]
        and checks["control_plane_executor"]
        and checks["workflows_module"]
        and checks["blackboard_module"]
        and checks["social_audit_module"]
        and failed_commands == 0
    ):
        autonomy_level = "level_3_assisted_execution_validated"

    return {
        "generated_at": utc_now_iso(),
        "project": "K-Atlas OS",
        "checkpoint": "30C",
        "name": "Autonomy Ladder Runner",
        "autonomy_level": autonomy_level,
        "summary": {
            "passed_commands": passed_commands,
            "failed_commands": failed_commands,
            "checks_ok": len([value for value in checks.values() if bool(value)]),
            "checks_total": len(checks),
        },
        "checks": checks,
        "commands": results,
        "next": [
            "Checkpoint 31: Instagram Oficial do K-Atlas - identidade e plano operacional",
            "Checkpoint 32: Creative Media Gateway geral",
            "Checkpoint 33: SaaS Builder Agent Bridge",
            "Checkpoint 34: Supervisor Autopilot",
            "Checkpoint 35: Credential Vault no Render validado",
            "Checkpoint 36: Sandbox API Adapter",
            "Checkpoint 37: AutoReporter central",
            "Checkpoint 38: SaaS Factory workflow real",
            "Checkpoint 39: Deploy pipeline assistido",
            "Checkpoint 40: K-Atlas Assisted Autonomy v1"
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# K-Atlas Autonomy Ladder Status",
        "",
        f"Generated at: {report['generated_at']}",
        f"Checkpoint: {report['checkpoint']} - {report['name']}",
        f"Autonomy level: {report['autonomy_level']}",
        "",
        "## Summary",
        "",
        f"- Passed commands: {report['summary']['passed_commands']}",
        f"- Failed commands: {report['summary']['failed_commands']}",
        f"- Checks OK: {report['summary']['checks_ok']} / {report['summary']['checks_total']}",
        "",
        "## Checks",
        "",
    ]

    for key, value in report["checks"].items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Next",
        "",
    ])

    for item in report["next"]:
        lines.append(f"- {item}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    python_exe = sys.executable

    commands = [
        [python_exe, "-m", "k_atlas.core.control_plane.smoke_test_control_plane"],
        [python_exe, "-m", "k_atlas.core.control_plane.smoke_test_control_plane_executor"],
        [python_exe, "-m", "k_atlas.core.workflows.smoke_test_agent_workflows"],
        [python_exe, "-m", "k_atlas.core.blackboard.smoke_test_blackboard"],
        [python_exe, "-m", "k_atlas.social.social_audit.smoke_test_social_audit_live"],
    ]

    results = []

    for command in commands:
        print("RUN:", " ".join(command))
        result = run_command(command)
        results.append(result)
        print("OK:" if result["ok"] else "FAIL:", result["command"])

    git_status = run_command(["git", "status", "--short"], timeout=60)
    git_log = run_command(["git", "log", "--oneline", "-5"], timeout=60)

    results.append(git_status)
    results.append(git_log)

    report = build_report(results)

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)

    print("")
    print("AUTONOMY_LEVEL:", report["autonomy_level"])
    print("REPORT_JSON:", REPORT_JSON)
    print("REPORT_MD:", REPORT_MD)

    if report["summary"]["failed_commands"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())