# -*- coding: utf-8 -*-
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

        cards = root / "k_atlas" / "lousa" / "cards"
        cards.mkdir(parents=True, exist_ok=True)

        (cards / "brics.json").write_text(
            json.dumps(
                {
                    "title": "Criar Product Spec supervisionado para BRICS Paraguay",
                    "description": "Marketplace Paraguay bilingue com Creative Brief e Specialist Council antes do scaffold.",
                    "lane": "backlog",
                    "status": "backlog",
                    "priority": "high",
                    "tags": ["brics", "marketplace", "paraguay", "governance"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = generate_next_prompt(root)

        assert_true(result["success"], "generate_next_prompt falhou")

        prompt = result["analysis"]["prompt_for_engineer"]

        assert_true("Creative Brief" in prompt, "Creative Brief ausente do prompt")
        assert_true("Specialist Council" in prompt, "Specialist Council ausente do prompt")
        assert_true("nao criar scaffold" in prompt.lower(), "bloqueio de scaffold ausente")
        assert_true(result["policy"]["can_execute_commands"] is False, "Prompt Generator nao pode executar comandos")

        print("Prompt Governance smoke test OK")
        print("next_step:", result["analysis"]["next_step_correct"])
