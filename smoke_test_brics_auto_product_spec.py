# -*- coding: utf-8 -*-
from pathlib import Path
import json

ROOT = Path.cwd()
SPEC = ROOT / "k_atlas" / "saas_factory" / "products" / "brics-paraguay-autos" / "product_spec.json"
MD = ROOT / "k_atlas" / "saas_factory" / "products" / "brics-paraguay-autos" / "product_spec.md"

if not SPEC.exists():
    raise SystemExit("product_spec.json nao existe")

if not MD.exists():
    raise SystemExit("product_spec.md nao existe")

data = json.loads(SPEC.read_text(encoding="utf-8"))

required = [
    "BRICS",
    "Paraguay",
    "automoveis",
    "ai_autofill",
    "dashboard_v1",
    "legal_tax_checklist",
    "human_approval_required_before_publish"
]

text = json.dumps(data, ensure_ascii=False).lower()

for item in required:
    if item.lower() not in text:
        raise SystemExit("Marcador ausente: " + item)

if data["ai_autofill"]["human_review_required"] is not True:
    raise SystemExit("IA precisa exigir revisao humana")

if data["governance"]["legal_review_required_before_real_launch"] is not True:
    raise SystemExit("review juridico precisa ser obrigatorio antes de lancamento real")

if data["governance"]["tax_review_required_before_monetization"] is not True:
    raise SystemExit("review tributario precisa ser obrigatorio antes de monetizacao")

if "pt" not in data["languages"] or "es" not in data["languages"]:
    raise SystemExit("produto precisa ser bilingue pt/es")

print("BRICS Paraguay Autos Product Spec smoke test OK")
print("next_step:", data["next_step_correct"])
