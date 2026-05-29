from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .spec import build_product_spec


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SaaSBuilderAgent:
    def __init__(self, output_root: str | Path = "k_atlas/saas_factory/products") -> None:
        self.output_root = Path(output_root)

    def create_product_structure(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        spec = build_product_spec(payload)
        product_dir = self.output_root / spec.slug

        for path in [
            product_dir,
            product_dir / "data",
            product_dir / "modules",
            product_dir / "tests",
            product_dir / "reports",
        ]:
            path.mkdir(parents=True, exist_ok=True)

        (product_dir / "product.json").write_text(
            json.dumps({
                "created_at": utc_now_iso(),
                "status": "scaffold_created",
                "spec": spec.to_dict(),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        (product_dir / "data" / "state.json").write_text(
            json.dumps({
                "product": spec.product_name,
                "metrics": {
                    "leads_today": 0,
                    "revenue_week": 0,
                    "pending_tasks": 0,
                },
                "leads": [],
                "tasks": [],
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        (product_dir / "modules" / "__init__.py").write_text("", encoding="utf-8")

        (product_dir / "modules" / "core.py").write_text(f'''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCT_NAME = "{spec.product_name}"
PRODUCT_SLUG = "{spec.slug}"

def load_state(path: str | Path = "data/state.json") -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {{"product": PRODUCT_NAME, "metrics": {{}}, "leads": [], "tasks": []}}
    return json.loads(target.read_text(encoding="utf-8"))

def summarize_product() -> dict[str, Any]:
    return {{
        "product": PRODUCT_NAME,
        "slug": PRODUCT_SLUG,
        "status": "mvp_scaffold_ready",
    }}
'''.lstrip(), encoding="utf-8")

        (product_dir / "app.py").write_text(f'''
from __future__ import annotations

import streamlit as st

from modules.core import load_state, summarize_product

st.set_page_config(page_title="{spec.product_name}", layout="wide")
st.title("{spec.product_name}")
st.caption("MVP gerado pelo K-Atlas SaaS Builder Agent.")

state = load_state()
summary = summarize_product()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Leads hoje", state.get("metrics", {{}}).get("leads_today", 0))

with col2:
    st.metric("Receita semana", state.get("metrics", {{}}).get("revenue_week", 0))

with col3:
    st.metric("Tarefas pendentes", state.get("metrics", {{}}).get("pending_tasks", 0))

st.divider()
st.subheader("Resumo")
st.json(summary)
st.subheader("Modulos planejados")
st.json({spec.modules!r})
'''.lstrip(), encoding="utf-8")

        (product_dir / "README.md").write_text(f'''
# {spec.product_name}

MVP gerado pelo K-Atlas SaaS Builder Agent.

## Problema
{spec.problem}

## Solucao
{spec.solution}

## Publico
{spec.audience}

## Monetizacao
{spec.monetization}

## Governanca
- Sem API externa por padrao.
- Sem token em texto puro.
- Revisao humana obrigatoria antes de deploy.
'''.lstrip(), encoding="utf-8")

        (product_dir / "tests" / "smoke_test.py").write_text('''
from __future__ import annotations

import py_compile
import unittest
from pathlib import Path

class ProductSmokeTest(unittest.TestCase):
    def test_files_exist(self) -> None:
        self.assertTrue(Path("app.py").exists())
        self.assertTrue(Path("product.json").exists())
        self.assertTrue(Path("modules/core.py").exists())

    def test_compile(self) -> None:
        py_compile.compile("app.py", doraise=True)
        py_compile.compile("modules/core.py", doraise=True)

if __name__ == "__main__":
    unittest.main(verbosity=2)
'''.lstrip(), encoding="utf-8")

        return {
            "ok": True,
            "status": "product_structure_created",
            "product_dir": str(product_dir).replace("\\", "/"),
            "spec": spec.to_dict(),
        }

    def generate_app_module(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        result = self.create_product_structure(payload)
        product_dir = Path(result["product_dir"])
        py_compile.compile(str(product_dir / "app.py"), doraise=True)
        py_compile.compile(str(product_dir / "modules" / "core.py"), doraise=True)
        result["status"] = "app_module_generated"
        result["compiled"] = True
        return result
