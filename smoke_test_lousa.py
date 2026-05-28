# -*- coding: utf-8 -*-
"""
Smoke test da Lousa Operacional.

Uso:
python smoke_test_lousa.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import k_atlas.lousa.lousa as lousa


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        original_root = lousa.ROOT
        original_lousa_dir = lousa.LOUSA_DIR
        original_boards_dir = lousa.BOARDS_DIR
        original_cards_dir = lousa.CARDS_DIR
        original_reviews_dir = lousa.REVIEWS_DIR

        lousa.ROOT = root
        lousa.LOUSA_DIR = root / "k_atlas" / "lousa"
        lousa.BOARDS_DIR = lousa.LOUSA_DIR / "boards"
        lousa.CARDS_DIR = lousa.LOUSA_DIR / "cards"
        lousa.REVIEWS_DIR = lousa.LOUSA_DIR / "reviews"

        try:
            board = lousa.create_board(
                title="Lousa Smoke Test",
                objective="Validar criacao de lousa operacional.",
                phase="smoke_test",
            )

            assert_true(board["success"], "board falhou")
            assert_true(Path(board["board_path"]).exists(), "board_path nao existe")

            card = lousa.add_card(
                title="Primeiro movimento",
                description="Registrar primeiro movimento operacional.",
                lane="doing",
                priority="high",
                tags=["smoke_test", "lousa"],
            )

            assert_true(card["success"], "card falhou")
            assert_true(Path(card["card_path"]).exists(), "card_path nao existe")

            snap = lousa.snapshot()

            assert_true(snap["success"], "snapshot falhou")
            assert_true(snap["totals"]["boards"] == 1, "total boards incorreto")
            assert_true(snap["totals"]["cards"] == 1, "total cards incorreto")
            assert_true(snap["policy"]["executes_commands"] is False, "lousa nao deve executar comandos")

            print("Lousa smoke test OK")

        finally:
            lousa.ROOT = original_root
            lousa.LOUSA_DIR = original_lousa_dir
            lousa.BOARDS_DIR = original_boards_dir
            lousa.CARDS_DIR = original_cards_dir
            lousa.REVIEWS_DIR = original_reviews_dir
