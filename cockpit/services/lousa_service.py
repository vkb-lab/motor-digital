# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cockpit Lousa Service

Leitura read-only da Lousa Operacional.
Nao executa comandos.
Nao altera codigo.
Nao aprova decisoes.
Nao aplica patches.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
LOUSA_DIR = ROOT / "k_atlas" / "lousa"
BOARDS_DIR = LOUSA_DIR / "boards"
CARDS_DIR = LOUSA_DIR / "cards"
REVIEWS_DIR = LOUSA_DIR / "reviews"


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


def load_folder(folder: Path, limit: int = 100) -> List[Dict[str, Any]]:
    folder.mkdir(parents=True, exist_ok=True)

    items: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*.json"))[-limit:]:
        items.append(
            {
                "name": path.name,
                "path": str(path),
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                "data": load_json(path),
            }
        )

    return items


def group_cards_by_lane(cards: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    lanes = {
        "backlog": [],
        "doing": [],
        "blocked": [],
        "done": [],
        "professor_review": [],
        "unknown": [],
    }

    for item in cards:
        data = item.get("data", {})
        lane = data.get("lane", "unknown") if isinstance(data, dict) else "unknown"

        if lane not in lanes:
            lane = "unknown"

        lanes[lane].append(data)

    return lanes


def collect_lousa_snapshot(limit: int = 100) -> Dict[str, Any]:
    boards = load_folder(BOARDS_DIR, limit=limit)
    cards = load_folder(CARDS_DIR, limit=limit)
    reviews = load_folder(REVIEWS_DIR, limit=limit)

    latest_board = boards[-1]["data"] if boards else {}
    lanes = group_cards_by_lane(cards)

    return {
        "success": True,
        "created_at": now_iso(),
        "root": str(ROOT),
        "lousa_dir": str(LOUSA_DIR),
        "totals": {
            "boards": len(boards),
            "cards": len(cards),
            "reviews": len(reviews),
            "backlog": len(lanes["backlog"]),
            "doing": len(lanes["doing"]),
            "blocked": len(lanes["blocked"]),
            "done": len(lanes["done"]),
            "professor_review": len(lanes["professor_review"]),
        },
        "latest_board": latest_board,
        "lanes": lanes,
        "data": {
            "boards": boards,
            "cards": cards,
            "reviews": reviews,
        },
        "policy": {
            "mode": "read-only",
            "can_execute_commands": False,
            "can_modify_code": False,
            "can_approve_decisions": False,
            "can_apply_patches": False,
            "requires_human_operator": True,
        },
    }
