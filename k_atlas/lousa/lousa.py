# -*- coding: utf-8 -*-
"""
K-Atlas OS - Lousa Operacional

A Lousa registra o estado estratégico-operacional do K-Atlas.

Ela NÃO executa comandos.
Ela NÃO altera código.
Ela NÃO aprova patches.

Ela organiza:
- estado atual
- próximo movimento
- bloqueios
- decisões pendentes
- avaliação do professor
- ligação com Cowork
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
LOUSA_DIR = ROOT / "k_atlas" / "lousa"
BOARDS_DIR = LOUSA_DIR / "boards"
CARDS_DIR = LOUSA_DIR / "cards"
REVIEWS_DIR = LOUSA_DIR / "reviews"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in [LOUSA_DIR, BOARDS_DIR, CARDS_DIR, REVIEWS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "lousa"


def create_board(title: str, objective: str, phase: str = "operation") -> Dict[str, Any]:
    ensure_dirs()

    board_id = str(uuid.uuid4())
    created_at = now_iso()

    data = {
        "board_id": board_id,
        "title": title,
        "objective": objective,
        "phase": phase,
        "status": "active",
        "created_at": created_at,
        "updated_at": created_at,
        "lanes": {
            "backlog": [],
            "doing": [],
            "blocked": [],
            "done": [],
            "professor_review": []
        },
        "policy": {
            "read_only_by_default": True,
            "requires_human_operator": True,
            "does_not_execute_commands": True,
            "does_not_apply_patches": True
        }
    }

    path = BOARDS_DIR / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + safe_slug(title) + ".json")
    write_json(path, data)

    return {
        "success": True,
        "message": "Lousa criada.",
        "board_path": str(path),
        "board": data
    }


def latest_board_path() -> Optional[Path]:
    ensure_dirs()
    boards = sorted(BOARDS_DIR.glob("*.json"))
    if not boards:
        return None
    return boards[-1]


def add_card(
    title: str,
    description: str,
    lane: str = "backlog",
    priority: str = "normal",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    ensure_dirs()

    board_path = latest_board_path()
    if board_path is None:
        created = create_board(
            title="Lousa Operacional K-Atlas",
            objective="Organizar próximos movimentos do K-Atlas OS.",
            phase="operation",
        )
        board_path = Path(created["board_path"])

    board = read_json(board_path)

    if lane not in board["lanes"]:
        raise ValueError("Lane invalida: " + lane)

    card_id = str(uuid.uuid4())
    created_at = now_iso()

    card = {
        "card_id": card_id,
        "title": title,
        "description": description,
        "lane": lane,
        "priority": priority,
        "tags": tags or [],
        "status": lane,
        "created_at": created_at,
        "updated_at": created_at,
    }

    board["lanes"][lane].append(card_id)
    board["updated_at"] = created_at

    card_path = CARDS_DIR / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + safe_slug(title) + ".json")

    write_json(card_path, card)
    write_json(board_path, board)

    return {
        "success": True,
        "message": "Card criado na Lousa.",
        "board_path": str(board_path),
        "card_path": str(card_path),
        "card": card
    }


def snapshot() -> Dict[str, Any]:
    ensure_dirs()

    boards = []
    cards = []
    reviews = []

    for path in sorted(BOARDS_DIR.glob("*.json")):
        boards.append({"path": str(path), "data": read_json(path)})

    for path in sorted(CARDS_DIR.glob("*.json")):
        cards.append({"path": str(path), "data": read_json(path)})

    for path in sorted(REVIEWS_DIR.glob("*.json")):
        reviews.append({"path": str(path), "data": read_json(path)})

    return {
        "success": True,
        "created_at": now_iso(),
        "totals": {
            "boards": len(boards),
            "cards": len(cards),
            "reviews": len(reviews)
        },
        "boards": boards,
        "cards": cards,
        "reviews": reviews,
        "policy": {
            "mode": "read-only-operational",
            "executes_commands": False,
            "applies_patches": False,
            "approves_changes": False
        }
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="K-Atlas Lousa Operacional")
    sub = parser.add_subparsers(dest="action", required=True)

    board = sub.add_parser("board")
    board.add_argument("--title", required=True)
    board.add_argument("--objective", required=True)
    board.add_argument("--phase", default="operation")

    card = sub.add_parser("card")
    card.add_argument("--title", required=True)
    card.add_argument("--description", required=True)
    card.add_argument("--lane", default="backlog")
    card.add_argument("--priority", default="normal")
    card.add_argument("--tags", default="")

    sub.add_parser("snapshot")

    return parser


def parse_tags(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "board":
        result = create_board(
            title=args.title,
            objective=args.objective,
            phase=args.phase,
        )
    elif args.action == "card":
        result = add_card(
            title=args.title,
            description=args.description,
            lane=args.lane,
            priority=args.priority,
            tags=parse_tags(args.tags),
        )
    elif args.action == "snapshot":
        result = snapshot()
    else:
        result = {"success": False, "message": "Acao desconhecida."}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
