
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from k_atlas.cowork.prompt_generator import collect_state, generate_next_prompt, status


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        (root / "reports" / "module_reports").mkdir(parents=True, exist_ok=True)
        (root / "reports" / "dev_runner_report.json").parent.mkdir(parents=True, exist_ok=True)
        (root / "reports" / "dev_runner_report.json").write_text(
            json.dumps({"success": True, "failed_required": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        cards = root / "k_atlas" / "lousa" / "cards"
        cards.mkdir(parents=True, exist_ok=True)
        (cards / "card.json").write_text(
            json.dumps(
                {
                    "title": "Integrar Lousa ao cockpit em modo read-only",
                    "description": "Mostrar Lousa sem executar comandos.",
                    "lane": "backlog",
                    "priority": "normal",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        sessions = root / "k_atlas" / "cowork" / "sessions"
        steps = root / "k_atlas" / "cowork" / "steps"
        reviews = root / "k_atlas" / "cowork" / "reviews"

        sessions.mkdir(parents=True, exist_ok=True)
        steps.mkdir(parents=True, exist_ok=True)
        reviews.mkdir(parents=True, exist_ok=True)

        (sessions / "session.json").write_text(
            json.dumps({"current_step": 10, "max_steps": 10, "status": "ready_for_review"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        (steps / "step.json").write_text(
            json.dumps({"step_number": 10, "status": "done"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        state = collect_state(root)
        assert_true(state["success"], "collect_state falhou")
        assert_true(state["dev_runner_report"]["success"] is True, "dev_runner nao foi lido")
        assert_true(len(state["lousa_cards"]) == 1, "lousa nao foi lida")

        result = generate_next_prompt(root)
        assert_true(result["success"], "generate falhou")
        assert_true(Path(result["recommendation_path"]).exists(), "recommendation nao criada")
        assert_true(Path(result["next_step_json_path"]).exists(), "next_step json nao criado")
        assert_true(Path(result["next_step_md_path"]).exists(), "next_step md nao criado")
        assert_true(result["policy"]["can_execute_commands"] is False, "nao pode executar comandos")
        assert_true(result["policy"]["can_modify_code"] is False, "nao pode modificar codigo")
        assert_true("prompt_for_engineer" in result["analysis"], "prompt ausente")

        check = status(root)
        assert_true(check["success"], "status falhou")
        assert_true(check["recommendations_total"] >= 1, "recomendacao nao registrada")

        print("Prompt Generator smoke test OK")
        print("next_step:", result["analysis"]["next_step_correct"])
        print("priority:", result["analysis"]["priority"])
        print("risk:", result["analysis"]["risk"])
