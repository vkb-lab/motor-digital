# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Prompt Generator Service

Leitura read-only do Cowork Prompt Generator.
Nao executa comandos.
Nao modifica codigo.
Nao envia prompt ao ChatGPT.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "k_atlas" / "cowork"
NEXT_STEPS_DIR = PROMPT_DIR / "next_steps"
RECOMMENDATIONS_DIR = PROMPT_DIR / "recommendations"


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


def load_markdown(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return "Erro ao ler Markdown: " + str(exc)


def load_json_folder(folder: Path, limit: int = 50) -> List[Dict[str, Any]]:
    folder.mkdir(parents=True, exist_ok=True)

    items: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*.json"))[-limit:]:
        md_path = path.with_suffix(".md")

        items.append(
            {
                "name": path.name,
                "path": str(path),
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                "data": load_json(path),
                "markdown_path": str(md_path) if md_path.exists() else None,
                "markdown": load_markdown(md_path) if md_path.exists() else "",
            }
        )

    return items


def collect_prompt_generator_snapshot(limit: int = 50) -> Dict[str, Any]:
    next_steps = load_json_folder(NEXT_STEPS_DIR, limit=limit)
    recommendations = load_json_folder(RECOMMENDATIONS_DIR, limit=limit)

    latest = recommendations[-1]["data"] if recommendations else {}
    latest_analysis = latest.get("analysis", {}) if isinstance(latest, dict) else {}

    return {
        "success": True,
        "created_at": now_iso(),
        "root": str(ROOT),
        "prompt_dir": str(PROMPT_DIR),
        "totals": {
            "next_steps": len(next_steps),
            "recommendations": len(recommendations),
        },
        "latest_analysis": latest_analysis,
        "latest_recommendation": latest,
        "data": {
            "next_steps": next_steps,
            "recommendations": recommendations,
        },
        "policy": {
            "mode": "read-only",
            "can_execute_commands": False,
            "can_modify_code": False,
            "can_apply_patches": False,
            "can_control_browser": False,
            "can_access_chatgpt": False,
            "requires_human_operator": True,
        },
    }
