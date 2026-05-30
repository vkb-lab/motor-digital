from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_count_json_list(path: str) -> int:
    target = Path(path)
    if not target.exists():
        return 0

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return 0

    return len(data) if isinstance(data, list) else 0


def safe_count_jsonl(path: str) -> int:
    target = Path(path)
    if not target.exists():
        return 0

    try:
        return len([line for line in target.read_text(encoding="utf-8").splitlines() if line.strip()])
    except Exception:
        return 0


def run_git(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()
    except Exception as exc:
        return f"git_error:{type(exc).__name__}:{exc}"


def path_exists(path: str) -> bool:
    return Path(path).exists()


def build_system_snapshot() -> dict[str, Any]:
    modules = {
        "control_plane": path_exists("k_atlas/core/control_plane"),
        "workflows": path_exists("k_atlas/core/workflows"),
        "blackboard": path_exists("k_atlas/core/blackboard"),
        "supervisor_autopilot": path_exists("k_atlas/core/supervisor_autopilot"),
        "credential_vault": path_exists("k_atlas/core/credential_vault"),
        "sandbox_api_adapter": path_exists("k_atlas/core/sandbox_api_adapter"),
        "creative_media_gateway": path_exists("k_atlas/creative/media_gateway"),
        "saas_builder": path_exists("k_atlas/saas_factory/builder_agent"),
        "social_audit": path_exists("k_atlas/social/social_audit"),
        "publishing_gateway": path_exists("k_atlas/social/publishing_gateway"),
    }

    pages = sorted([str(path).replace("\\", "/") for path in Path("pages").glob("*.py")]) if Path("pages").exists() else []

    snapshot = {
        "generated_at": utc_now_iso(),
        "project": "K-Atlas OS",
        "checkpoint": "37",
        "module": "AutoReporter Central",
        "git": {
            "branch": run_git(["branch", "--show-current"]),
            "last_commits": run_git(["log", "--oneline", "-10"]),
            "status_short": run_git(["status", "--short"]),
        },
        "modules": modules,
        "metrics": {
            "modules_ok": len([value for value in modules.values() if value]),
            "modules_total": len(modules),
            "streamlit_pages": len(pages),
            "control_plane_events": safe_count_jsonl("memory/control_plane/events.jsonl"),
            "supervisor_queue_items": safe_count_json_list("memory/control_plane/supervisor_queue.json"),
            "blackboard_messages": safe_count_json_list("memory/blackboard/messages.json"),
            "blackboard_commands": safe_count_json_list("memory/blackboard/command_queue.json"),
            "sandbox_api_requests": safe_count_json_list("memory/sandbox_api_adapter/requests.json"),
        },
        "pages": pages,
        "autonomy_status": {
            "current_level": "level_3_assisted_execution",
            "next_target": "level_4_limited_real_publish_after_vault_api_and_approval",
            "guardrails": [
                "sem publicação oficial automática",
                "sem token em texto puro",
                "sem browser automation para conta oficial",
                "sem mensagem em massa",
                "human review obrigatório para risco médio/alto",
            ],
        },
        "next_checkpoints": [
            "38 - SaaS Factory workflow real",
            "39 - Deploy pipeline assistido",
            "40 - K-Atlas Assisted Autonomy v1",
        ],
    }

    return snapshot
