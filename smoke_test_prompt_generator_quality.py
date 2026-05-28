
# -*- coding: utf-8 -*-
"""
Smoke test de qualidade do Prompt Generator.

Valida:
- cards genericos nao devem vencer cards especificos
- cards concluidos devem ser ignorados
- Prompt Generator permanece analysis-only

Uso:
python smoke_test_prompt_generator_quality.py
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from k_atlas.cowork.prompt_generator import generate_next_prompt


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        reports = root / "reports"
        reports.mkdir(parents=True, exist_ok=True)
        (reports / "dev_runner_report.json").write_text(
            json.dumps({"success": True, "failed_required": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        cards_dir = root / "k_atlas" / "lousa" / "cards"
        cards_dir.mkdir(parents=True, exist_ok=True)

        (cards_dir / "generic_done.json").write_text(
            json.dumps(
                {
                    "title": "Proximo movimento seguro",
                    "description": "Card generico ja concluido.",
                    "lane": "done",
                    "status": "done",
                    "priority": "normal",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        (cards_dir / "generic_backlog.json").write_text(
            json.dumps(
                {
                    "title": "Proximo movimento seguro",
                    "description": "Card generico ainda aberto.",
                    "lane": "backlog",
                    "status": "backlog",
                    "priority": "normal",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        (cards_dir / "specific_backlog.json").write_text(
            json.dumps(
                {
                    "title": "Integrar LearningAgent ao cockpit em modo read-only",
                    "description": "Exibir playbooks, lessons, training e errors sem executar comandos.",
                    "lane": "backlog",
                    "status": "backlog",
                    "priority": "high",
                    "tags": ["learning", "cockpit", "read-only"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = generate_next_prompt(root)

        assert_true(result["success"], "generate_next_prompt falhou")
        assert_true(result["policy"]["can_execute_commands"] is False, "Prompt Generator nao pode executar comandos")
        assert_true(result["policy"]["can_modify_code"] is False, "Prompt Generator nao pode modificar codigo")

        next_step = result["analysis"]["next_step_correct"]

        assert_true(
            next_step == "Integrar LearningAgent ao cockpit em modo read-only",
            "Prompt Generator escolheu card errado: " + next_step,
        )

        assert_true(Path(result["recommendation_path"]).exists(), "recommendation_path nao existe")
        assert_true(Path(result["next_step_md_path"]).exists(), "next_step_md_path nao existe")

        print("Prompt Generator quality smoke test OK")
        print("next_step:", next_step)
        print("risk:", result["analysis"]["risk"])
        print("priority:", result["analysis"]["priority"])
