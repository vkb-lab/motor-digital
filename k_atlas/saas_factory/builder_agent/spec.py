from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "k-atlas-product"


@dataclass(frozen=True)
class SaaSProductSpec:
    product_name: str
    slug: str
    audience: str
    problem: str
    solution: str
    monetization: str
    modules: list[str] = field(default_factory=list)
    governance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_product_spec(payload: Mapping[str, Any] | None = None) -> SaaSProductSpec:
    data = dict(payload or {})
    product_name = str(data.get("product_name") or data.get("name") or "K-Atlas MVP").strip()
    slug = str(data.get("slug") or slugify(product_name)).strip()

    modules = data.get("modules") or ["dashboard", "crm_light", "content_generator", "reports", "admin"]
    if not isinstance(modules, list):
        modules = [str(modules)]

    return SaaSProductSpec(
        product_name=product_name,
        slug=slugify(slug),
        audience=str(data.get("audience") or "empreendedores e operadores digitais"),
        problem=str(data.get("problem") or "processos manuais e baixa automacao"),
        solution=str(data.get("solution") or "MVP Streamlit com IA assistida e dados JSON"),
        monetization=str(data.get("monetization") or "assinatura mensal"),
        modules=[str(item) for item in modules],
        governance={
            "official_publish": False,
            "external_api_enabled": False,
            "human_review_required": True,
            "generated_by": "k_saas_builder",
        },
    )
