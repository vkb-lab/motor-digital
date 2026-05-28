
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from k_atlas.creative_intelligence.creative_brief import generate


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        source = Path.cwd() / "k_atlas" / "creative_intelligence" / "knowledge"
        target = root / "k_atlas" / "creative_intelligence" / "knowledge"
        target.mkdir(parents=True, exist_ok=True)

        for file in source.glob("*.json"):
            shutil.copy2(file, target / file.name)

        closet = generate("closet-pilot-winter-2026", root)
        brics = generate("brics-paraguay-marketplace", root)

        assert_true(closet["success"], "brief Closet Pilot falhou")
        assert_true(brics["success"], "brief BRICS falhou")

        assert_true(Path(closet["json_path"]).exists(), "json Closet ausente")
        assert_true(Path(closet["md_path"]).exists(), "md Closet ausente")
        assert_true(Path(brics["json_path"]).exists(), "json BRICS ausente")
        assert_true(Path(brics["md_path"]).exists(), "md BRICS ausente")

        closet_brief = closet["brief"]
        brics_brief = brics["brief"]

        assert_true("inverno 2026" == closet_brief["season"], "season incorreta")
        assert_true("burgundy" == closet_brief["palette"]["primary"], "paleta feminina incorreta")
        assert_true("green" == brics_brief["palette"]["primary"], "paleta BRICS incorreta")
        assert_true("yellow" == brics_brief["palette"]["secondary"], "secundaria BRICS incorreta")

        legal = " ".join(brics_brief.get("legal_guardrail", [])).lower()
        assert_true("nao copiar olx" in legal, "guardrail OLX ausente")

        assert_true(closet_brief["name_analysis"]["score"] >= 7, "score Closet baixo")
        assert_true(brics_brief["name_analysis"]["score"] >= 7, "score BRICS baixo")

        print("Creative Intelligence smoke test OK")
        print("closet:", closet["brief"]["next_product_move"])
        print("brics:", brics["brief"]["next_product_move"])
