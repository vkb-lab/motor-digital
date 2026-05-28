# -*- coding: utf-8 -*-
"""
Smoke test do Cowork Mode.

Uso:
python smoke_test_cowork.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import k_atlas.cowork.cowork as cowork


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        original_root = cowork.ROOT
        original_cowork_dir = cowork.COWORK_DIR
        original_sessions_dir = cowork.SESSIONS_DIR
        original_steps_dir = cowork.STEPS_DIR
        original_reviews_dir = cowork.REVIEWS_DIR

        cowork.ROOT = root
        cowork.COWORK_DIR = root / "k_atlas" / "cowork"
        cowork.SESSIONS_DIR = cowork.COWORK_DIR / "sessions"
        cowork.STEPS_DIR = cowork.COWORK_DIR / "steps"
        cowork.REVIEWS_DIR = cowork.COWORK_DIR / "reviews"

        try:
            started = cowork.start_session(
                goal="Validar fluxo cowork supervisionado.",
                max_steps=2,
            )
            assert_true(started["success"], "start_session falhou")
            assert_true(Path(started["session_path"]).exists(), "session nao criada")

            step1 = cowork.add_step(
                title="Criar comando de teste",
                command="python smoke_test.py",
                result_summary="Executado com sucesso.",
                status="done",
                risk="low",
            )
            assert_true(step1["success"], "step1 falhou")

            step2 = cowork.add_step(
                title="Validar review",
                command="python review.py",
                result_summary="Review pronto.",
                status="done",
                risk="low",
            )
            assert_true(step2["success"], "step2 falhou")
            assert_true(step2["session_status"] == "ready_for_review", "sessao deveria estar pronta para review")

            review = cowork.review_session()
            assert_true(review["success"], "review falhou")
            assert_true(Path(review["review_path"]).exists(), "review nao criado")
            assert_true(review["review"]["score"] == 10.0, "score deveria ser 10.0")

            status = cowork.get_status()
            assert_true(status["success"], "status falhou")
            assert_true(status["session"]["current_step"] == 2, "current_step incorreto")

            print("Cowork smoke test OK")

        finally:
            cowork.ROOT = original_root
            cowork.COWORK_DIR = original_cowork_dir
            cowork.SESSIONS_DIR = original_sessions_dir
            cowork.STEPS_DIR = original_steps_dir
            cowork.REVIEWS_DIR = original_reviews_dir
