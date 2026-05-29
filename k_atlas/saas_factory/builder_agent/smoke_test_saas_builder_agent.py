from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.saas_factory.builder_agent.builder import SaaSBuilderAgent
from k_atlas.saas_factory.builder_agent.spec import build_product_spec, slugify


class SaaSBuilderAgentSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_saas_builder_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def payload(self) -> dict:
        return {
            "product_name": "Teste SaaS Builder",
            "audience": "Founders",
            "problem": "Validar MVP rapido",
            "solution": "Cockpit Streamlit modular",
            "monetization": "assinatura",
            "modules": ["dashboard", "reports", "admin"],
        }

    def test_slugify(self) -> None:
        self.assertEqual(slugify("Teste SaaS Builder!"), "teste-saas-builder")

    def test_build_product_spec(self) -> None:
        spec = build_product_spec(self.payload())
        self.assertEqual(spec.slug, "teste-saas-builder")
        self.assertIn("dashboard", spec.modules)

    def test_create_product_structure(self) -> None:
        builder = SaaSBuilderAgent(output_root=self.tmp)
        result = builder.create_product_structure(self.payload())
        self.assertTrue(result["ok"])
        product_dir = Path(result["product_dir"])
        self.assertTrue((product_dir / "app.py").exists())
        self.assertTrue((product_dir / "product.json").exists())
        self.assertTrue((product_dir / "modules" / "core.py").exists())

    def test_generate_app_module_compiles(self) -> None:
        builder = SaaSBuilderAgent(output_root=self.tmp)
        result = builder.generate_app_module(self.payload())
        self.assertTrue(result["ok"])
        self.assertTrue(result["compiled"])

    def test_page_compiles(self) -> None:
        self.assertTrue(Path("pages/14_K_Atlas_SaaS_Builder.py").exists())
        py_compile.compile("pages/14_K_Atlas_SaaS_Builder.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
