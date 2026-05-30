from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCT_NAME = "K-Atlas Local Business Copilot"
PRODUCT_SLUG = "k-atlas-local-business-copilot"

def load_state(path: str | Path = "data/state.json") -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {"product": PRODUCT_NAME, "metrics": {}, "leads": [], "tasks": []}
    return json.loads(target.read_text(encoding="utf-8"))

def summarize_product() -> dict[str, Any]:
    return {
        "product": PRODUCT_NAME,
        "slug": PRODUCT_SLUG,
        "status": "mvp_scaffold_ready",
    }
