# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Cowork Service

Leitura read-only do Cowork Mode.
Nao executa comandos.
Nao controla navegador.
Nao altera arquivos.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
COWORK_DIR = ROOT / "k_atlas" / "cowork"

FOLDERS = {
    "sessions": COWORK_DIR / "sessions",
    "steps": COWORK_DIR / "steps",
    "reviews": COWORK_DIR / "reviews",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "error": str(exc),
            "path": str(path),
        }


def load_folder(folder: Path, limit: int = 50) -> List[Dict[str, Any]]:
    folder.mkdir(parents=True, exist_ok=True)

    items: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*.json"))[-limit:]:
        data = load_json(path)
        items.append(
            {
                "name": path.name,
                "path": str(path),
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                "data": data,
            }
        )

    return items


def collect_cowork_snapshot(limit: int = 50) -> Dict[str, Any]:
    data = {
        name: load_folder(path, limit=limit)
        for name, path in FOLDERS.items()
    }

    sessions = data.get("sessions", [])
    latest_session = sessions[-1]["data"] if sessions else {}

    steps = latest_session.get("steps", []) if isinstance(latest_session, dict) else []
    max_steps = latest_session.get("max_steps", 10) if isinstance(latest_session, dict) else 10
    current_step = latest_session.get("current_step", 0) if isinstance(latest_session, dict) else 0

    progress = 0
    if max_steps:
        progress = round((int(current_step) / int(max_steps)) * 100, 1)

    done = [
        step for step in steps
        if isinstance(step, dict) and step.get("status") in ["done", "ok", "success"]
    ]

    failed = [
        step for step in steps
        if isinstance(step, dict) and step.get("status") in ["failed", "error"]
    ]

    return {
        "success": True,
        "created_at": now_iso(),
        "root": str(ROOT),
        "cowork_dir": str(COWORK_DIR),
        "totals": {
            name: len(items)
            for name, items in data.items()
        },
        "latest_session": latest_session,
        "progress": {
            "current_step": current_step,
            "max_steps": max_steps,
            "progress_percent": progress,
            "done": len(done),
            "failed": len(failed),
            "pending": max(0, int(max_steps) - int(current_step)),
        },
        "data": data,
        "policy": {
            "mode": "read-only",
            "can_execute_command": False,
            "can_control_browser": False,
            "can_apply_patch": False,
            "requires_human_operator": True,
        },
    }
