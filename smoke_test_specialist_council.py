
# -*- coding: utf-8 -*-
from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from k_atlas.specialist_council.council import generate_from_preset


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        source = Path.cwd() / "k_atlas" / "specialist_council"
        target = root / "k_atlas" / "specialist_council"
        target.mkdir(parents=True, exist_ok=True)

        for name in ["specialist_registry.json", "decision_rules.json"]:
            shutil.copy2(source / name, target / name)

        result = generate_from_preset("brics-paraguay-marketplace", root)

        assert_true(result["success"], "review falhou")
        assert_true(Path(result["json_path"]).exists(), "json nao criado")
        assert_true(Path(result["md_path"]).exists(), "md nao criado")

        review = result["review"]
        ids = [item["id"] for item in review["required_specialists"]]

        assert_true("marketplace_agent" in ids, "marketplace_agent ausente")
        assert_true("localization_agent" in ids, "localization_agent ausente")
        assert_true("legal_context_agent" in ids, "legal_context_agent ausente")
        assert_true("tax_context_agent" in ids, "tax_context_agent ausente")
        assert_true("dashboard_scale_agent" in ids, "dashboard_scale_agent ausente")
        assert_true(review["governance"]["scaffold_allowed_now"] is False, "scaffold nao deve estar liberado")
        assert_true("multilingual" in review["checklists"], "checklist multilingual ausente")
        assert_true(review["risk"]["level"] in ["medium", "high"], "risco deveria ser medio ou alto")

        print("Specialist Council smoke test OK")
        print("specialists:", len(ids))
        print("risk:", review["risk"]["level"])
