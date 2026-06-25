from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

CORE_PATHS = [
    ("KOS Operator Chat", "pages/KOS_Operator_Chat.py", "page"),
    ("KOS Unified Command Cockpit", "pages/KOS_Unified_Command_Cockpit.py", "page"),
    ("KOS Runtime Health", "pages/KOS_Runtime_Health.py", "page"),
    ("KOS Mission Queue", "pages/KOS_Mission_Queue.py", "page"),
    ("KOS Safe Execution Review", "pages/KOS_Safe_Execution_Review.py", "page"),
    ("KOS Human Approval", "pages/KOS_Human_Approval.py", "page"),
    ("KOS Gmail Status", "reports/KOS_GMAIL_REAL_CONNECTION_STATUS.md", "read_only_report"),
    ("KOS Google Toolbelt Status", "memory/kos_governance/KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json", "read_only_registry"),
    ("KOS Brain Provider Status", "memory/kos_governance/KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json", "read_only_registry"),
    ("KOS Render Read-Only Mobile Runtime", "app_render.py", "app_reference"),
]

SCRIPT_PATHS = [
    ("Brain Provider status script", "scripts/run_kos_brain_provider_status.py"),
    ("Google AI Toolbelt bridge", "scripts/run_google_ai_toolbelt_bridge.py"),
    ("Gmail operator bridge", "scripts/run_gmail_operator.py"),
]


def run_git(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", "--no-pager", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except Exception as exc:
        return f"GIT_STATUS_ERROR: {exc.__class__.__name__}"
    return (completed.stdout or completed.stderr or "").strip()


def file_status(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    return {
        "path": relative_path,
        "exists": path.exists(),
        "kind": "file" if path.is_file() else "missing",
    }


def build_status() -> dict[str, Any]:
    branch = run_git(["branch", "--show-current"])
    status_short = run_git(["status", "--short"])

    blocks = []
    core_paths: dict[str, dict[str, Any]] = {}
    for name, relative_path, kind in CORE_PATHS:
        item = file_status(relative_path)
        item.update({"name": name, "kind": kind})
        blocks.append(item)
        core_paths[relative_path] = item

    scripts = []
    for name, relative_path in SCRIPT_PATHS:
        item = file_status(relative_path)
        item.update({"name": name, "kind": "script"})
        scripts.append(item)

    pages_dir = ROOT / "pages"
    page_count = len(list(pages_dir.glob("*.py"))) if pages_dir.exists() else 0

    core_found = sum(1 for item in blocks if item["exists"])

    return {
        "status": "KOS_LOCAL_HOME_STATUS_READY",
        "entrypoint": "app.py",
        "home": "K-OS Local Command Center",
        "recommended_port": 8501,
        "git": {
            "branch": branch,
            "dirty": bool(status_short.strip()),
            "status_short": status_short,
        },
        "summary": {
            "core_total": len(blocks),
            "core_found": core_found,
            "script_total": len(scripts),
            "script_found": sum(1 for item in scripts if item["exists"]),
            "streamlit_pages_count": page_count,
            "legacy_sidebar_warning": page_count > len(blocks),
        },
        "blocks": blocks,
        "scripts": scripts,
        "core_paths": core_paths,
        "guardrails": {
            "gmail_api_called": False,
            "external_action_executed": False,
            "secrets_read": False,
            "legacy_pages_deleted": False,
        },
    }


def main() -> None:
    print(json.dumps(build_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
