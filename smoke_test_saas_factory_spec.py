# -*- coding: utf-8 -*-
"""
Smoke test da SaaS Factory Product Spec.

Uso:
python smoke_test_saas_factory_spec.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import k_atlas.saas_factory.product_spec as product_spec


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        original_root = product_spec.ROOT
        original_products_dir = product_spec.PRODUCTS_DIR

        product_spec.ROOT = root
        product_spec.PRODUCTS_DIR = root / "k_atlas" / "saas_factory" / "products"

        try:
            spec = product_spec.build_wardrobe_product_spec()
            result = product_spec.save_spec(spec)

            assert_true(result["success"], "save_spec falhou")
            assert_true(Path(result["json_path"]).exists(), "product_spec.json nao existe")
            assert_true(Path(result["md_path"]).exists(), "product_spec.md nao existe")
            assert_true(spec["name"] == "Closet Pilot", "nome incorreto")
            assert_true("guarda-roupa" in spec["problem"].lower(), "problema nao fala de guarda-roupa")
            assert_true(spec["policy"]["can_deploy"] is False, "nao pode fazer deploy agora")
            assert_true(spec["next_step_correct"], "proximo passo correto ausente")

            print("SaaS Factory product spec smoke test OK")
            print("product:", spec["name"])
            print("next_step:", spec["next_step_correct"])

        finally:
            product_spec.ROOT = original_root
            product_spec.PRODUCTS_DIR = original_products_dir
